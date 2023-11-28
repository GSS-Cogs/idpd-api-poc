from src.validation import validate_time



def test_check_time_validation():
    """this funciton will test the pydantic time validation"""

    time_value = "2023-11-29 16:00:00"

    assert validate_time(time_value)