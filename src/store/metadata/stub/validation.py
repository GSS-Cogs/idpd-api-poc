import json
from pathlib import Path
from typing import Dict, List

import schemas
from data import process_json_files


def _validate_resource_count(resource_dict: Dict, resource_name: str):
    """
    Check that the sub document of a json file has a length that matches the count field of that json file.
    """
    if len(resource_dict[resource_name]) != int(resource_dict["count"]):
        raise ValueError(
            f"""
        The `count` field for {resource_name} is wrong.
        Got: {int(resource_dict["count"])}.
        Expected: {len(resource_dict[resource_name])}.
        """
        )


def _validate_resource_identifier_type_and_schema(resource_dict, resource_type, schema):
    """
    Validate resource identifier and type, and validate against schema.
    """
    # Check that `@id` and `identifier` are consistent
    for resource in resource_dict[resource_type]:
        if resource["@id"].split("/")[-1] != resource["identifier"]:
            raise ValueError(
                f"""
            Mismatch between '@id' and 'identifier' fields:

            @id: {resource['@id'].split("/")[-1]}

            identifier: {resource['identifier']}
            """
            )

        # Check that the resource type is in the path
        # eg an id for a topic should have /topics in the url
        if resource_type not in resource["@id"]:
            raise ValueError(
                f"""
            The @id for a resource of type `{resource_type}` should contain
            /{resource_type} in the URL, but does not.

            Got: {resource["@id"]}
            """
            )

    # Schema validation
    schema(**resource_dict)


def _validate_edition_in_dataset(datasets: Dict, edition: Dict):
    """
    Editions sub documents are included in two places within our stubbed data content:
    1. A short form representation of an edition is included in a "editions" sub-document within the dataset json file.
    2. The full edition document is included in the edition json file.

    With this check we are making sure that the field values in the short form edition match the fields in the full edition document.
    """

    for id, issued, modified, in_series in [
        (edn["@id"], edn["issued"], edn["modified"], edn["in_series"])
        for edn in edition["editions"]
    ]:
        # Confirm that the `in_series` reference is pointing to the
        # same series as specified by the id
        if not id.startswith(in_series):
            raise ValueError(
                f"""
            The `in_series` field should appear at the beginning of the `@id` field but does not. This is a data error.

            @id: {id}
            in_series: {in_series}
            """
            )

        # Use the `in_series` field to pull the correct parent dataset document from all datasets.
        parent_dataset = [
            dataset for dataset in datasets["datasets"] if dataset["@id"] == in_series
        ]
        if len(parent_dataset) != 1:
            raise ValueError(
                f"Cannot find exactly one parent dataset with an @id of {in_series}"
            )
        parent_dataset = parent_dataset[0]

        # Now get the short form editions from that dataset document
        short_form_editions = parent_dataset["editions"]

        # Using our list of short form editions docs, confirm there is exactly one short form
        # editional document (from those listed in the dataset) with the same @id as the long form
        # representation from the editions file.
        short_form_editions_with_correct_id = [
            x for x in short_form_editions if x["@id"] == id
        ]

        if len(short_form_editions_with_correct_id) != 1:
            raise ValueError(
                f"""
            Could not find exactly one edition listed at the dataset level that
            has the @id of:

            {id}

            Found {len(short_form_editions_with_correct_id)} matching editions in parent dataset:
            {parent_dataset["@id"]}.

            The truncated editions listed for this dataset are:
            {json.dumps(short_form_editions, indent=2)}
            """
            )
        short_form_edition_with_correct_id = short_form_editions_with_correct_id[0]

        # Confirm the issued date matches
        if issued != short_form_edition_with_correct_id["issued"]:
            raise ValueError(
                f"""
            For the version {id}.

            The issued date in the full version document is {issued}.

            But in the truncated view at the dataset level it is {short_form_edition_with_correct_id["issued"]}.

            These fields should match.
            """
            )

        # Confirm the modified date matches
        if modified != short_form_edition_with_correct_id["modified"]:
            raise ValueError(
                f"""
            For the version {id}.

            The modified date in the full version document is {modified}.

            But in the truncated view at the dataset level it is {short_form_edition_with_correct_id["modified"]}.

            These fields should match.
            """
            )

        if len(short_form_edition_with_correct_id) != 3:
            raise ValueError(
                f"""The version:

                {json.dumps(short_form_edition_with_correct_id, indent=2)}

            Should have three fields, "@id", "issued" and "modified" but has more.
            """
            )


def _validate_version_in_edition(
    version: List[Dict], versions_in_edition: Dict[str, Dict]
):
    """
    Versions sub documents are included in two places witin our stubbed data
    content.

    1. A short form representation of a version is included in a "versions" sub
       document within the edition json file for the relevant edition.
    2. The full version documents is included in the versions json file.

    With this check we are making sure that the field values as inlcuded in the
    short form version match the fields as included in the full version document.
    """
    if version["@id"] not in versions_in_edition.keys():
        raise ValueError(
            f"Version @id {version['@id']} not found in {versions_in_edition.keys()}"
        )
    for id, issued in [(x["@id"], x["issued"]) for x in version["versions"]]:
        # The version id includes the path to its edition so get all
        # the short form version information we processed at the edition level
        version_path = "/".join(id.split("/")[:-1])
        versions_for_this_edition = versions_in_edition.get(version_path, None)

        # Now we have a list of all relevant short form version docs, confirm there is
        # exactly one short form version document (from the editions file) with the
        # same @id as the long form representation from the versions file.
        short_form_versions_with_correct_id = [
            x for x in versions_for_this_edition if x["@id"] == id
        ]
        if len(short_form_versions_with_correct_id) != 1:
            raise ValueError(
                f"""
            Could not find exactly one version listed at the edition level that has the @id of {id}.

            Found {len(short_form_versions_with_correct_id)} versions.

            The truncated versions listed for this edition are:
            {versions_for_this_edition}
            """
            )
        short_form_version_with_correct_id = short_form_versions_with_correct_id[0]

        # Confirm the issued date matches
        if issued != short_form_version_with_correct_id["issued"]:
            raise ValueError(
                f"""
            For the version {id}.

            The issued date in the full version document is {issued}.

            But in the truncated view at the editions level it is {short_form_version_with_correct_id["issued"]}.

            These fields should match.
            """
            )

        if len(short_form_version_with_correct_id) != 2:
            raise ValueError(
                f"""The version:

            {json.dumps(short_form_version_with_correct_id, indent=2)}

            Should only have two fields, "@id" and "issued" but has more.
            """
            )


def validate_datasets(datasets):
    _validate_resource_count(datasets, "datasets")
    _validate_resource_identifier_type_and_schema(
        datasets, "datasets", schemas.Datasets
    )


def validate_editions(
    datasets,
    editions,
    dataset_editions_urls,
    versions_in_edition,
    topics_in_editions,
    dataset_publishers,
):
    for edition in editions:
        _validate_resource_count(edition, "editions")
        _validate_resource_identifier_type_and_schema(
            edition, "editions", schemas.Editions
        )
        # TODO Move this to _assert_edition_in_dataset?
        if edition["@id"] not in dataset_editions_urls:
            raise ValueError(
                f"Editions URL {edition['@id']} not found in {dataset_editions_urls}"
            )
        for edn in edition["editions"]:
            versions_in_edition[edn["versions_url"]] = edn["versions"]
            topics_in_editions.update(edn["topics"])
            if edn["publisher"] not in dataset_publishers:
                raise ValueError(
                    f"{edn['publisher']} not in publisher list {dataset_publishers}"
                )
        _validate_edition_in_dataset(datasets, edition)


def validate_versions(versions, versions_in_edition):
    for version in versions:
        _validate_resource_count(version, "versions")
        _validate_resource_identifier_type_and_schema(
            version, "versions", schemas.Versions
        )
        _validate_version_in_edition(version, versions_in_edition)


def validate_topics(datasets, topics, topics_in_editions):
    _validate_resource_count(topics, "topics")
    _validate_resource_identifier_type_and_schema(topics, "topics", schemas.Topics)
    topic_ids = [topic["@id"] for topic in topics["topics"]]
    for dataset in datasets["datasets"]:
        for topic in dataset["topics"]:
            if topic not in topic_ids:
                raise ValueError(f"{topic} not in list of approved topics {topic_ids}")
    for topic in topics_in_editions:
        if topic not in topic_ids:
            raise ValueError(
                f"""
            Topic {topic} defined within edition but it is not (and must be) defined as a topic resource in topics.json.

            Defined topics from topics.json:
            {topic_ids}"""
            )


def validate_publishers(
    publishers: Dict, dataset_publishers: List[Dict], dataset_creators: List[Dict]
):
    """
    Confirm that:
    - any publisher listed at the `datasets` level exists
    - any creator listed at the `datasets` level exists
    - all publisher resources appear in one or more of the above checks
    """
    _validate_resource_count(publishers, "publishers")
    publisher_ids_from_publishers_json = [x["@id"] for x in publishers["publishers"]]
    references_used = []

    for publisher in dataset_publishers:
        if publisher not in publisher_ids_from_publishers_json:
            raise ValueError(
                f"""
            The publisher: {publisher}
            is referenced in a datasets resource but does not exist in the definitions of publishers from publishers.json.
            """
            )
        references_used.append(publisher)

    for publisher in dataset_creators:
        if publisher not in publisher_ids_from_publishers_json:
            raise ValueError(
                f"""
            The publisher: {publisher}
            is referenced in a datasets resource but does not exist in the definitions of publishers.
            """
            )
        references_used.append(publisher)

    # At this point all publishers we've defined should have appeared at least once.
    unique_references_used = list(set(references_used))

    unique_references_used.sort()
    publisher_ids_from_publishers_json.sort()

    if len(unique_references_used) != len(publisher_ids_from_publishers_json):
        raise ValueError(
            f"""
        Publishers are being created that do not appear to be utilised.

        IDs of publisher resources being created:
        {publisher_ids_from_publishers_json}

        IDs of publisher resources being used:
        {unique_references_used}
        """
        )

    # Schema validation
    schemas.Publishers(**publishers)


# Specify locations of JSON files
metadata_stub_content_path = Path("src/store/metadata/stub/content").absolute()
datasets_source_path = Path(metadata_stub_content_path / "datasets.json")
editions_source_path = Path(metadata_stub_content_path / "editions")
versions_source_path = Path(metadata_stub_content_path / "editions" / "versions")
topics_source_path = Path(metadata_stub_content_path / "topics.json")
publishers_source_path = Path(metadata_stub_content_path / "publishers.json")

# Load datasets json file from disk
with open(datasets_source_path) as f:
    datasets_source_dict = json.load(f)

# Load editions json files from disk
editions = process_json_files(editions_source_path)

# Load versions json files from disk
versions = process_json_files(versions_source_path)

# Load topics json file from disk
with open(topics_source_path) as f:
    topics_source_dict = json.load(f)

# Load publishers json file from disk
with open(publishers_source_path) as f:
    publishers_source_dict = json.load(f)

# Extract edition URLs from datasets.json for validation later
dataset_editions_urls = [
    dataset["editions_url"] for dataset in datasets_source_dict["datasets"]
]

# Extract publishers from datasets.json for validation later
dataset_publishers = {
    dataset["publisher"] for dataset in datasets_source_dict["datasets"]
}

# Extract creators from datasets.json for validation later
dataset_creators = {dataset["creator"] for dataset in datasets_source_dict["datasets"]}

# Empty dict to hold version data from editions for validation later
versions_in_edition = dict()

# Empty set to hold topic data from editions for validation later
topics_in_editions = set()

if __name__ == "__main__":
    validate_datasets(datasets_source_dict)
    validate_editions(
        datasets_source_dict,
        editions,
        dataset_editions_urls,
        versions_in_edition,
        topics_in_editions,
        dataset_publishers,
    )
    validate_versions(versions, versions_in_edition)
    validate_topics(datasets_source_dict, topics_source_dict, topics_in_editions)
    validate_publishers(publishers_source_dict, dataset_publishers, dataset_creators)
