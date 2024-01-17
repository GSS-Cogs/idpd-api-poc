import pytest
from pathlib import Path
import json

from src.data import _assert_editions_ordered_by_issued


def test_editions_ordered_by_issued_fail():
    """
    This test will check if the this the editions subtopic is ordered by issued
    (has to be longer than 1), the test is expected to fail
    """
    try:
        file_path = Path("tests/test_jsons/datasets_dummy_fail.json").absolute()

        with open(file_path) as f:
            datasets_source_dict = json.load(f)
        _assert_editions__ordered_by_issued(datasets_source_dict, "datasets","editions")
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
    

    _assert_editions_ordered_by_issued(datasets_source_dict, "datasets","editions")



def test_verisons_ordered_by_issued_fail():
    """
    This test will check if the this the versions subtopic is ordered by issued
    (has to be longer than 1), the test is expected to fail
    """
    try:
        file_path = Path("tests/test_jsons/versions_dummy_data_fail.json").absolute()

        with open(file_path) as f:
            datasets_source_dict = json.load(f)
        _assert_editions_ordered_by_issued(datasets_source_dict, "editions","versions")
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
    

    _assert_editions_ordered_by_issued(datasets_source_dict,"editions" ,"versions")