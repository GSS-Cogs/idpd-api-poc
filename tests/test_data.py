import pytest
from pathlib import Path
import json

from src.data import _assert_ordered_by_issued


def test_ordered_by_issued_fail():
    """This test will check if the this issued firt value is the most recent"""
    try:
        file_path = Path("src/store/metadata/stub/content/datasets_dummy_fail.json").absolute()

        with open(file_path) as f:
            datasets_source_dict = json.load(f)
        _assert_ordered_by_issued(datasets_source_dict, "editions")
    except:
        "The datasets should be ordered by 'issued' (from most recent)" 


def test_ordered_by_issued_succeed():
    """This test will check if the this issued firt value is the most recent"""

    file_path = Path("src/store/metadata/stub/content/datasets_dummy_correct.json").absolute()

    with open(file_path) as f:
        datasets_source_dict = json.load(f)
    

    assert _assert_ordered_by_issued(datasets_source_dict, "editions")