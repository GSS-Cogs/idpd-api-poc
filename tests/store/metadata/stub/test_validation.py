import json
from pathlib import Path

import pytest
from store.metadata.stub.validation import (
    _validate_edition_in_dataset,
    _validate_version_in_edition,
    _validate_resource_count,
    _validate_resource_identifier_type_and_schema,
    validate_editions,
    validate_publishers,
    validate_topics,
)
import schemas


def test_validate_resource_count():
    file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets_invalid_resource_count.json"
    )
    with open(file_path) as f:
        datasets = json.load(f)
    with pytest.raises(ValueError) as exc:
        _validate_resource_count(datasets, "datasets")
    assert (
        "The `count` field for datasets is wrong.\n        Count: 2.\n        Number of datasets: 1."
        in str(exc.value)
    )


def test_validate_resource_identifier():
    file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets_invalid_identifier.json"
    )
    with open(file_path) as f:
        datasets = json.load(f)
    with pytest.raises(ValueError) as exc:
        _validate_resource_identifier_type_and_schema(
            datasets, "datasets", schemas.Datasets
        )
    assert (
        "Mismatch between '@id' and 'identifier' fields:\n            @id: https://staging.idpd.uk/datasets/ciph\n            identifier: cpih"
        in str(exc.value)
    )


def test_validate_resource_type():
    file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets_invalid_type.json"
    )
    with open(file_path) as f:
        datasets = json.load(f)
    with pytest.raises(ValueError) as exc:
        _validate_resource_identifier_type_and_schema(
            datasets, "datasets", schemas.Datasets
        )
    assert (
        "The @id for a resource of type `datasets` should contain\n            /datasets in the URL, but does not.\n\n            @id: https://staging.idpd.uk/cpih"
        in str(exc.value)
    )


def test_validate_edition_in_dataset_id_not_in_dataset():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition_id_not_in_dataset.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        "Editions URL https://staging.idpd.uk/datasets/ciph/editions not found"
    ) in str(exc.value)


def test_validate_edition_in_dataset_id_not_in_series():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition_id_not_in_series.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        "The `in_series` value should appear at the beginning of the `@id` value but does not.\n            @id: https://staging.idpd.uk/datasets/ciph/editions/2022-01\n            in_series: https://staging.idpd.uk/datasets/cpih"
    ) in str(exc.value)


def test_validate_edition_in_dataset_no_parent_dataset():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition_invalid_parent_dataset.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        "Cannot find exactly one parent dataset with an `@id` value of https://staging.idpd.uk/datasets/ciph"
    ) in str(exc.value)


def test_validate_edition_in_dataset_invalid_date_order():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets_with_multiple_editions_invalid_order.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        "Editions at the dataset level should be sorted from newest to oldest."
    ) in str(exc.value)


def test_validate_edition_in_dataset_invalid_summarised_edition_id():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets_invalid_summarised_edition_id.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        'Could not find exactly one edition listed at the dataset level with an `@id` of https://staging.idpd.uk/datasets/cpih/editions/2022-01.\n            Found 0 matching editions in parent dataset https://staging.idpd.uk/datasets/cpih.\n            The summarised editions listed for this dataset are:\n            [\n  {\n    "@id": "https://staging.idpd.uk/datasets/ciph/editions/2022-01",\n    "issued": "2022-01-01T00:00:00Z",\n    "modified": "2022-01-12T00:00:00Z"\n  }\n]'
    ) in str(exc.value)


def test_validate_edition_in_dataset_invalid_issued_date():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition_invalid_issued_date.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        "For edition https://staging.idpd.uk/datasets/cpih/editions/2022-01, the `issued` date in the full edition document is 2023-01-01T00:00:00Z.\n            But in the summarised edition at the dataset level the `issued` date is 2022-01-01T00:00:00Z.\n            These fields should match."
    ) in str(exc.value)


def test_validate_edition_in_dataset_invalid_modified_date():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition_invalid_modified_date.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        "For edition https://staging.idpd.uk/datasets/cpih/editions/2022-01, the `modified` date in the full edition document is 2023-01-12T00:00:00Z.\n            But in the summarised edition at the dataset level the `modified` date is 2022-01-12T00:00:00Z.\n            These fields should match."
    ) in str(exc.value)


def test_validate_edition_in_dataset_additional_summarised_edition_field():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets_additional_summarised_edition_field.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        'The edition https://staging.idpd.uk/datasets/cpih/editions/2022-01 should have three fields, "@id", "issued" and "modified" but has more:\n\n            {\n  "@id": "https://staging.idpd.uk/datasets/cpih/editions/2022-01",\n  "issued": "2022-01-01T00:00:00Z",\n  "modified": "2022-01-12T00:00:00Z",\n  "extra": "field"\n}'
    ) in str(exc.value)


def test_validate_version_in_edition_invalid_version_id():
    versions_in_edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions_in_editions/versions_in_editions.json"
    )
    version_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions/version_invalid_id.json"
    )
    with open(versions_in_edition_file_path) as f:
        versions_in_editions = json.load(f)
    with open(version_file_path) as f:
        version = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_version_in_edition(version, versions_in_editions)
    assert (
        "Version @id https://staging.idpd.uk/datasets/ciph/editions/2022-01/versions not found"
        in str(exc.value)
    )


def test_validate_version_in_edition_invalid_date_order():
    versions_in_edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions_in_editions/versions_in_editions_multiple_versions_invalid_order.json"
    )
    version_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions/version.json"
    )
    with open(versions_in_edition_file_path) as f:
        versions_in_editions = json.load(f)
    with open(version_file_path) as f:
        version = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_version_in_edition(version, versions_in_editions)
    assert (
        "Versions at the edition level should be sorted from newest to oldest."
        in str(exc.value)
    )


def test_validate_version_in_edition_multiple_versions_same_id():
    versions_in_edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions_in_editions/versions_in_editions_multiple_versions_with_same_id.json"
    )
    version_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions/version.json"
    )
    with open(versions_in_edition_file_path) as f:
        versions_in_editions = json.load(f)
    with open(version_file_path) as f:
        version = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_version_in_edition(version, versions_in_editions)
    assert (
        "Could not find exactly one version listed at the edition level with an `@id` of https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1.\n            Found 2 versions.\n            The summarised versions listed for this edition are:\n            [{'@id': 'https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1', 'issued': '2022-01-01T00:00:00Z'}, {'@id': 'https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1', 'issued': '2022-01-01T00:00:00Z'}]"
    ) in str(exc.value)


def test_validate_version_in_edition_invalid_issued_date():
    versions_in_edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions_in_editions/versions_in_editions_invalid_issued_date.json"
    )
    version_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions/version.json"
    )
    with open(versions_in_edition_file_path) as f:
        versions_in_editions = json.load(f)
    with open(version_file_path) as f:
        version = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_version_in_edition(version, versions_in_editions)
    assert (
        "For version https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1, the `issued` date in the full version document is 2022-01-01T00:00:00Z.\n            But in the summarised version at the editions level the `issued` date is 2023-01-01T00:00:00Z.\n            These fields should match."
    ) in str(exc.value)


def test_validate_version_in_edition_additional_field():
    versions_in_edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions_in_editions/versions_in_editions_additional_field.json"
    )
    version_file_path = Path(
        "tests/store/metadata/stub/test-cases/versions/version.json"
    )
    with open(versions_in_edition_file_path) as f:
        versions_in_editions = json.load(f)
    with open(version_file_path) as f:
        version = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_version_in_edition(version, versions_in_editions)
    assert (
        'The version https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1 should have two fields, "@id" and "issued" but has more:\n\n            {\n  "@id": "https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1",\n  "issued": "2022-01-01T00:00:00Z",\n  "extra": "field"\n}'
    ) in str(exc.value)


def test_validate_publishers_in_editions():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)
    editions = [edition]
    dataset_publishers = {"publisher1", "publisher2"}
    dataset_creators = {"creator1", "creator2"}
    with pytest.raises(ValueError) as exc:
        validate_editions(datasets, editions, dataset_publishers, dataset_creators)
    assert (
        "https://staging.idpd.uk/publishers/office-for-national-statistics not in publisher list"
    ) in str(exc.value)


def test_validate_creators_in_editions():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets.json"
    )
    edition_file_path = Path(
        "tests/store/metadata/stub/test-cases/editions/edition.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(edition_file_path) as f:
        edition = json.load(f)

    editions = [edition]
    dataset_publishers = {
        "https://staging.idpd.uk/publishers/office-for-national-statistics"
    }
    dataset_creators = {"creator1", "creator2"}
    with pytest.raises(ValueError) as exc:
        validate_editions(datasets, editions, dataset_publishers, dataset_creators)
    assert (
        "https://staging.idpd.uk/publishers/office-for-national-statistics not in creator list"
    ) in str(exc.value)


def test_validate_topics_in_dataset():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets.json"
    )
    topics_file_path = Path(
        "tests/store/metadata/stub/test-cases/topics_not_in_dataset.json"
    )
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(topics_file_path) as f:
        topics = json.load(f)
    topics_in_editions = {
        "https://staging.idpd.uk/topics/it-and-internet-industry",
        "https://staging.idpd.uk/topics/business-trade-and-international-development",
    }

    with pytest.raises(ValueError) as exc:
        validate_topics(datasets, topics, topics_in_editions)
    assert (
        "https://staging.idpd.uk/topics/economy not in list of approved topics"
    ) in str(exc.value)


def test_validate_topics_in_edition():
    datasets_file_path = Path(
        "tests/store/metadata/stub/test-cases/datasets/datasets.json"
    )
    topics_file_path = Path("tests/store/metadata/stub/test-cases/topics.json")
    with open(datasets_file_path) as f:
        datasets = json.load(f)
    with open(topics_file_path) as f:
        topics = json.load(f)
    topics_in_editions = {
        "https://staging.idpd.uk/topics/invalid-topic",
    }
    with pytest.raises(ValueError) as exc:
        validate_topics(datasets, topics, topics_in_editions)
    assert (
        "Topic https://staging.idpd.uk/topics/invalid-topic defined within edition but it is not (and must be) defined as a topic resource in topics.json."
    ) in str(exc.value)


def test_validate_dataset_publishers():
    publishers_file_path = Path("tests/store/metadata/stub/test-cases/publishers.json")
    with open(publishers_file_path) as f:
        publishers = json.load(f)
    dataset_publishers = {"https://staging.idpd.uk/publishers/invalid-publisher"}
    dataset_creators = {
        "https://staging.idpd.uk/publishers/department-for-education",
        "https://staging.idpd.uk/publishers/office-for-national-statistics",
        "https://staging.idpd.uk/publishers/ofcom",
    }
    with pytest.raises(ValueError) as exc:
        validate_publishers(publishers, dataset_publishers, dataset_creators)
    assert (
        "The publisher: https://staging.idpd.uk/publishers/invalid-publisher\n            is referenced in a datasets resource but does not exist in the definitions of publishers from publishers.json."
    ) in str(exc.value)


def test_validate_dataset_creators():
    publishers_file_path = Path("tests/store/metadata/stub/test-cases/publishers.json")
    with open(publishers_file_path) as f:
        publishers = json.load(f)
    dataset_publishers = {
        "https://staging.idpd.uk/publishers/office-for-national-statistics"
    }
    dataset_creators = {"https://staging.idpd.uk/publishers/invalid-creator"}
    with pytest.raises(ValueError) as exc:
        validate_publishers(publishers, dataset_publishers, dataset_creators)
    assert (
        "The creator https://staging.idpd.uk/publishers/invalid-creator is referenced in a datasets resource but does not exist in the definitions of publishers from publishers.json."
    ) in str(exc.value)


def test_validate_publishers_referenced():
    publishers_file_path = Path(
        "tests/store/metadata/stub/test-cases/publishers_not_referenced.json"
    )
    with open(publishers_file_path) as f:
        publishers = json.load(f)
    dataset_publishers = {
        "https://staging.idpd.uk/publishers/office-for-national-statistics"
    }
    dataset_creators = {
        "https://staging.idpd.uk/publishers/department-for-education",
        "https://staging.idpd.uk/publishers/office-for-national-statistics",
        "https://staging.idpd.uk/publishers/ofcom",
    }
    with pytest.raises(ValueError) as exc:
        validate_publishers(publishers, dataset_publishers, dataset_creators)
    assert ("Publishers are being created that do not appear to be utilised.") in str(
        exc.value
    )
