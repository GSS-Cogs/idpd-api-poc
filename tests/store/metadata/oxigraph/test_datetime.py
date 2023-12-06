from src.validation import validate_time



def test_check_time_validation_valid():
    """this funciton will test the pydantic time validation"""

    time_value = "2023-11-29 16:00:00"

    assert validate_time(time_value) == "2023-11-29 16:00:00"

def test_check_time_validation_unvalid():
    """this funciton will test the pydantic time
     validation with an unvalid value"""

    time = "2023-11-SS 16:00:00"
    try:
        raise validate_time(time)
    except ValueError as x:
        x == "The valid time format is 'YYYY-MM-DD %H%M%S'"
