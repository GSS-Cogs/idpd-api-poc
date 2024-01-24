import pytest
from pathlib import Path
import json

from src.store.metadata.stub.validation import (
    _assert_editions_ordered_by_issued,
    _validate_edition_in_dataset,
    _validate_version_in_edition,
)


def test_validate_edition_in_dataset():
    with open(
        "tests/store/metadata/stub/test-cases/datasets_with_multiple_editions.json"
    ) as f:
        datasets = json.load(f)
    with open(
        "tests/store/metadata/stub/test-cases/edition_with_multiple_versions.json"
    ) as f:
        edition = json.load(f)
    with pytest.raises(ValueError) as exc:
        _validate_edition_in_dataset(datasets, edition)


def test_validate_version_in_edition():
    with open("tests/store/metadata/stub/test-cases/version.json") as f:
        version = json.load(f)
    with open(
        "tests/store/metadata/stub/test-cases/versions_in_editions_multiple_versions_invalid_order.json"
    ) as f:
        versions_in_edition = json.load(f)
    with pytest.raises(ValueError) as exc:
        _validate_version_in_edition(version, versions_in_edition)


def test_editions_ordered_by_issued_fail():
    """
    This test will check if the this the editions subtopic is ordered by issued
    (has to be longer than 1), the test is expected to fail
    """
    try:
        file_path = Path("tests/test_jsons/datasets_dummy_fail.json").absolute()

        with open(file_path) as f:
            datasets_source_dict = json.load(f)
        _assert_editions_ordered_by_issued(datasets_source_dict, "datasets", "editions")
    except:
        "The datasets should be ordered by 'issued' (from most recent)"


def test_editions_ordered_by_issued_succeed():
    """
    This test will check if the this the editions subtopic is ordered by issued
    (has to be longer than 1), the test is expected to pass
    """

    file_path = Path("tests/test_jsons/datasets_dummy_correct.json").absolute()

    with open(file_path) as f:
        datasets_source_dict = json.load(f)

    _assert_editions_ordered_by_issued(datasets_source_dict, "datasets", "editions")


def test_verisons_ordered_by_issued_fail():
    """
    This test will check if the this the versions subtopic is ordered by issued
    (has to be longer than 1), the test is expected to fail
    """
    try:
        file_path = Path("tests/test_jsons/versions_dummy_data_fail.json").absolute()

        with open(file_path) as f:
            datasets_source_dict = json.load(f)
        _assert_editions_ordered_by_issued(datasets_source_dict, "editions", "versions")
    except:
        "The datasets should be ordered by 'issued' (from most recent)"


def test_versions_ordered_by_issued_succeed():
    """
    This test will check if the this the editions subtopic is ordered by issued
    (has to be longer than 1), the test is expected to pass
    """

    file_path = Path("tests/test_jsons/versions_dummy_data_correct.json").absolute()

    with open(file_path) as f:
        datasets_source_dict = json.load(f)

    _assert_editions_ordered_by_issued(datasets_source_dict, "editions", "versions")
