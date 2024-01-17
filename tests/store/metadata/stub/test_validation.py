import json

import pytest
from store.metadata.stub.validation import (
    _validate_edition_in_dataset,
    # _validate_version_in_edition,
    # _validate_resource_count,
    # _validate_resource_identifier_and_type,
    # _validate_publisher,
)


# TODO Delete once tests added
def test_validate_edition_in_dataset():
    with open("tests/store/metadata/stub/test-cases/datasets.json") as f:
        datasets = json.load(f)
    with open("tests/store/metadata/stub/test-cases/edition.json") as f:
        edition = json.load(f)
    _validate_edition_in_dataset(datasets, edition)


def test_validate_edition_in_dataset_id_not_in_series():
    with open("tests/store/metadata/stub/test-cases/datasets.json") as f:
        datasets = json.load(f)
    with open(
        "tests/store/metadata/stub/test-cases/edition_id_not_in_series.json"
    ) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        "The `in_series` field should appear at the beginning of the `@id` field but does not. This is a data error.\n\n            @id: https://staging.idpd.uk/datasets/ciph/editions/2022-01\n            in_series: https://staging.idpd.uk/datasets/cpih"
    ) in str(exc.value)


def test_validate_edition_in_dataset_no_parent_dataset():
    with open("tests/store/metadata/stub/test-cases/datasets.json") as f:
        datasets = json.load(f)
    with open(
        "tests/store/metadata/stub/test-cases/edition_wrong_parent_dataset.json"
    ) as f:
        edition = json.load(f)

    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)

    assert (
        "Cannot find exactly one parent dataset with an @id of https://staging.idpd.uk/datasets/ciph"
    ) in str(exc.value)
