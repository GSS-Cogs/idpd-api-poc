from sqlite3 import Date
from pydantic import validator

from datetime import datetime



@validator('time')
def validate_time(cls, time_value):
    try:
        #Format should be "YYYY-MM-DD %H%M%S"
        datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')
        return time_value
    except ValueError:
        return ValueError