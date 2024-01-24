import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

import schemas
from data import process_json_files


def _validate_resource_count(resource_dict: Dict, resource_name: str):
    """
    Check that the length of a sub-document in a json file matches the `count` field of the json file.
    """
    if len(resource_dict[resource_name]) != int(resource_dict["count"]):
        raise ValueError(
            f"""
        The `count` field for {resource_name} is wrong.
        Count: {int(resource_dict["count"])}.
        Number of {resource_name}: {len(resource_dict[resource_name])}.
        """
        )


def _validate_resource_identifier_type_and_schema(
    resource_dict: Dict, resource_type: str, schema
):
    """
    Validate resource identifier and type, and validate against schema model.
    """
    for resource in resource_dict[resource_type]:
        # Check that `@id` and `identifier` are consistent
        if resource["@id"].split("/")[-1] != resource["identifier"]:
            raise ValueError(
                f"""
            Mismatch between '@id' and 'identifier' fields:
            @id: {resource['@id']}
            identifier: {resource['identifier']}
            """
            )

        # Check that the resource type is in the path
        # e.g. the @id for a topic should have "/topics" in the URL
        if resource_type not in resource["@id"]:
            raise ValueError(
                f"""
            The @id for a resource of type `{resource_type}` should contain
            /{resource_type} in the URL, but does not.

            @id: {resource["@id"]}
            """
            )

    # Schema validation
    schema(**resource_dict)


def _validate_edition_in_dataset(datasets: Dict, edition: Dict):
    """
    Editions sub-documents are included in two places within our stubbed data content:
    1. A summarised edition is included in the `editions` sub-document within the `datasets.json` file.
    2. The full edition document is included in the `edition.json` file.

    This check ensures that the field values in the summarised edition sub-document match the fields in the full edition document.
    """
    dataset_editions_urls = [
        dataset["editions_url"] for dataset in datasets["datasets"]
    ]
    if edition["@id"] not in dataset_editions_urls:
        raise ValueError(
            f"Editions URL {edition['@id']} not found in {dataset_editions_urls}"
        )
    for id, issued, modified, in_series in [
        (edn["@id"], edn["issued"], edn["modified"], edn["in_series"])
        for edn in edition["editions"]
    ]:
        # Confirm that the `in_series` value references the same series as specified in the `@id` value
        if not id.startswith(in_series):
            raise ValueError(
                f"""
            The `in_series` value should appear at the beginning of the `@id` value but does not.
            @id: {id}
            in_series: {in_series}
            """
            )

        # Use the `in_series` field to extract the parent dataset from all datasets.
        parent_dataset = [
            dataset for dataset in datasets["datasets"] if dataset["@id"] == in_series
        ]
        if len(parent_dataset) != 1:
            raise ValueError(
                f"Cannot find exactly one parent dataset with an `@id` value of {in_series}"
            )

        # Get the summarised editions from the parent dataset
        parent_dataset = parent_dataset[0]
        summarised_editions = parent_dataset["editions"]

        # Check that summarised editions are listed in date order from newest to oldest
        issued_dates = [edn["issued"] for edn in summarised_editions]
        sorted_issued_dates = sorted(
            issued_dates,
            reverse=True,
            key=lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z"),
        )
        if issued_dates != sorted_issued_dates:
            raise ValueError(
                "Editions at the dataset level should be sorted from newest to oldest."
            )

        # Confirm there is exactly one summarised edition with the same `@id` as the long form representation from the `editions.json` file.
        summarised_editions_for_edition_id = [
            edn for edn in summarised_editions if edn["@id"] == id
        ]

        if len(summarised_editions_for_edition_id) != 1:
            raise ValueError(
                f"""
            Could not find exactly one edition listed at the dataset level with an `@id` of {id}.
            Found {len(summarised_editions_for_edition_id)} matching editions in parent dataset {parent_dataset["@id"]}.
            The summarised editions listed for this dataset are:
            {json.dumps(summarised_editions, indent=2)}
            """
            )
        summarised_edition_for_edition_id = summarised_editions_for_edition_id[0]

        # Confirm the `issued` date matches
        if issued != summarised_edition_for_edition_id["issued"]:
            raise ValueError(
                f"""
            For edition {id}, the `issued` date in the full edition document is {issued}.
            But in the summarised edition at the dataset level the `issued` date is {summarised_edition_for_edition_id["issued"]}.
            These fields should match.
            """
            )

        # Confirm the `modified` date matches
        if modified != summarised_edition_for_edition_id["modified"]:
            raise ValueError(
                f"""
            For edition {id}, the `modified` date in the full edition document is {modified}.
            But in the summarised edition at the dataset level the `modified` date is {summarised_edition_for_edition_id["modified"]}.
            These fields should match.
            """
            )

        # Confirm that the summarised edition only consists of three fields (`@id`, `issued` and `modified`)
        if len(summarised_edition_for_edition_id) != 3:
            raise ValueError(
                f"""The edition {id} should have three fields, "@id", "issued" and "modified" but has more:

            {json.dumps(summarised_edition_for_edition_id, indent=2)}
            """
            )


def _validate_version_in_edition(version: Dict, versions_in_editions: Dict):
    """
    Versions sub-documents are included in two places within our stubbed data content.
    1. A summarised version is included in the `versions` sub-document within the `edition.json` file for the relevant edition.
    2. The full version document is included in the `version.json` file.

    This check ensures that the field values in the summarised version sub-document match the fields in the full version document.
    """
    if version["@id"] not in versions_in_editions.keys():
        raise ValueError(
            f"Version @id {version['@id']} not found in {list(versions_in_editions.keys())}"
        )
    for id, issued in [(vsn["@id"], vsn["issued"]) for vsn in version["versions"]]:
        # The `version` @id includes the path to its edition the version_url field) so get the summarised version information from the versions_in_editions dictionary
        version_path = "/".join(id.split("/")[:-1])
        versions_for_this_edition = versions_in_editions.get(version_path, None)

        # Check that summarised versions are listed in date order from newest to oldest
        issued_dates = [vsn["issued"] for vsn in versions_for_this_edition]
        sorted_issued_dates = sorted(
            issued_dates,
            reverse=True,
            key=lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S%z"),
        )
        if issued_dates != sorted_issued_dates:
            raise ValueError(
                "Versions at the edition level should be sorted from newest to oldest."
            )
        ###

        # Confirm there is exactly one summarised version with the same `@id` as the long form representation from the `versions.json` file.
        summarised_versions_for_version_id = [
            vsn for vsn in versions_for_this_edition if vsn["@id"] == id
        ]
        if len(summarised_versions_for_version_id) != 1:
            raise ValueError(
                f"""
            Could not find exactly one version listed at the edition level with an `@id` of {id}.
            Found {len(summarised_versions_for_version_id)} versions.
            The summarised versions listed for this edition are:
            {versions_for_this_edition}
            """
            )
        summarised_version_for_version_id = summarised_versions_for_version_id[0]

        # Confirm the `issued` date matches
        if issued != summarised_version_for_version_id["issued"]:
            raise ValueError(
                f"""
            For version {id}, the `issued` date in the full version document is {issued}.
            But in the summarised version at the editions level the `issued` date is {summarised_version_for_version_id["issued"]}.
            These fields should match.
            """
            )
        # Confirm that the summarised version only consists of two fields (`@id` and `issued`)
        if len(summarised_version_for_version_id) != 2:
            raise ValueError(
                f"""The version {id} should have two fields, "@id" and "issued" but has more:

            {json.dumps(summarised_version_for_version_id, indent=2)}
            """
            )


def validate_datasets(datasets):
    _validate_resource_count(datasets, "datasets")
    _validate_resource_identifier_type_and_schema(
        datasets, "datasets", schemas.Datasets
    )


def validate_editions(datasets, editions, dataset_publishers, dataset_creators):
    for edition in editions:
        _validate_resource_count(edition, "editions")
        _validate_resource_identifier_type_and_schema(
            edition, "editions", schemas.Editions
        )
        for edn in edition["editions"]:
            if edn["publisher"] not in dataset_publishers:
                raise ValueError(
                    f"{edn['publisher']} not in publisher list {dataset_publishers}"
                )
            if edn["creator"] not in dataset_creators:
                raise ValueError(
                    f"{edn['creator']} not in creator list {dataset_creators}"
                )
        _validate_edition_in_dataset(datasets, edition)


def validate_versions(versions: List[Dict], versions_in_editions: Dict):
    for version in versions:
        _validate_resource_count(version, "versions")
        _validate_resource_identifier_type_and_schema(
            version, "versions", schemas.Versions
        )
        _validate_version_in_edition(version, versions_in_editions)


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
    publishers: Dict, dataset_publishers: Set, dataset_creators: Set
):
    """
    Confirm that:
    - any publisher listed at the `datasets` level exists
    - any creator listed at the `datasets` level exists
    - all publisher resources appear in one or more of the above checks
    """
    _validate_resource_count(publishers, "publishers")
    publisher_ids = [publisher["@id"] for publisher in publishers["publishers"]]
    publishers_referenced = []

    for publisher in dataset_publishers:
        if publisher not in publisher_ids:
            raise ValueError(
                f"""
            The publisher: {publisher}
            is referenced in a datasets resource but does not exist in the definitions of publishers from publishers.json.
            """
            )
        publishers_referenced.append(publisher)

    for creator in dataset_creators:
        if creator not in publisher_ids:
            raise ValueError(
                f"""
            The creator {creator} is referenced in a datasets resource but does not exist in the definitions of publishers from publishers.json.
            """
            )
        publishers_referenced.append(creator)

    # At this point all publishers we've defined should have appeared at least once.
    unique_publishers_referenced = list(set(publishers_referenced))

    unique_publishers_referenced.sort()
    publisher_ids.sort()

    if len(unique_publishers_referenced) != len(publisher_ids):
        raise ValueError(
            f"""
        Publishers are being created that do not appear to be utilised.

        IDs of publisher resources being created:
        {publisher_ids}

        IDs of publisher resources being used:
        {unique_publishers_referenced}
        """
        )

    # Schema validation
    schemas.Publishers(**publishers)


def _assert_editions_ordered_by_issued(list_of_datasets, main_dict: str, sub_dict: str):
    """
    this function will assert that the list of datasets subtset
    is ordered by issued, raises error if not
    """

    index = 0

    list_of_issued = []

    for dataset_dict in list_of_datasets[main_dict]:
        if len(dataset_dict[sub_dict]) > 1 and dataset_dict[sub_dict] is not None:
            for y in dataset_dict[sub_dict]:
                if index == 0:
                    first_value = dataset_dict[sub_dict][0]["issued"]
                fornow = y["issued"]
                list_of_issued.append(fornow)
                index += 1

            most_recent = max(list_of_issued)
            assert (
                first_value == most_recent
            ), "The datasets should be ordered by 'issued' (from most recent)"


def _assert_versions_ordered_by_issued(datasets, sub_dict: str):
    """
    this function will assert that the list of datasets subset
    is ordered by issued, raises error if not
    """

    index = 0

    list_of_issued = []

    if len(datasets[sub_dict]) > 1 and datasets[sub_dict] is not None:
        for dataset in datasets[sub_dict]:
            if index == 0:
                first_value = datasets[sub_dict][0]["issued"]
            fornow = dataset["issued"]
            list_of_issued.append(fornow)
            index += 1

        most_recent = max(list_of_issued)
        assert (
            first_value == most_recent
        ), "The datasets should be ordered by 'issued' (from most recent)"


# Specify locations of JSON files
metadata_stub_content_path = Path("src/store/metadata/stub/content").absolute()
datasets_source_path = Path(metadata_stub_content_path / "datasets.json")
editions_source_path = Path(metadata_stub_content_path / "editions")
versions_source_path = Path(metadata_stub_content_path / "editions" / "versions")
topics_source_path = Path(metadata_stub_content_path / "topics.json")
publishers_source_path = Path(metadata_stub_content_path / "publishers.json")

# Load JSON files from disk
with open(datasets_source_path) as f:
    datasets_source_dict = json.load(f)

editions = process_json_files(editions_source_path)

versions = process_json_files(versions_source_path)

with open(topics_source_path) as f:
    topics_source_dict = json.load(f)

with open(publishers_source_path) as f:
    publishers_source_dict = json.load(f)

# Extract publishers and creators from datasets.json for validation later
dataset_publishers = {
    dataset["publisher"] for dataset in datasets_source_dict["datasets"]
}

dataset_creators = {dataset["creator"] for dataset in datasets_source_dict["datasets"]}

# Extract version and topic data from editions for validation later
versions_in_editions = dict()
topics_in_editions = set()
for edition in editions:
    for edn in edition["editions"]:
        versions_in_editions[edn["versions_url"]] = edn["versions"]
        topics_in_editions.update(edn["topics"])


if __name__ == "__main__":
    validate_datasets(datasets_source_dict)
    validate_editions(
        datasets_source_dict, editions, dataset_publishers, dataset_creators
    )
    validate_versions(versions, versions_in_editions)
    validate_topics(datasets_source_dict, topics_source_dict, topics_in_editions)
    validate_publishers(publishers_source_dict, dataset_publishers, dataset_creators)
