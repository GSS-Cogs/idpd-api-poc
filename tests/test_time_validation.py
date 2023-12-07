import pytest
from src.validation import validate_time

from src.schemas import PeriodOfTime


def test_time_validation():
    time1 = "2022-09-30T23:59:00Z"
    time2 = "2022-09-01T00:00:00"
    time3 = "some non time data"
    test_class = PeriodOfTime(start=time3, end=time2)

    assert test_class.start == "this"

