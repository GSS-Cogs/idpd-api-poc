from sqlite3 import Date
from pydantic import validate_call

from datetime import datetime



@validate_call
def validate_time(time_value):
    try:
        #Format should be "YYYY-MM-DD %H%M%S"
        datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')
        return time_value
    except ValueError:
        return ValueError("The valid time format is 'YYYY-MM-DD %H%M%S'")