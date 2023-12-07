from sqlite3 import Date

from pydantic import AwareDatetime
from datetime import datetime



def validate_time(cls, time_value: str) -> str:
    try:
        fornow = time_value
        #Format should be "YYYY-MM-DD %H%M%S"
        datetime.strptime(fornow, '%Y-%m-%dT%H:%M:%SZ')
        if not fornow.endswith('Z') or fornow[10] == 'T':
            raise ValueError("The valid time format is 'YYYY-MM-DDT%H%M%SZ'")
        return fornow
    except ValueError:
        raise ValueError("The valid time format is 'YYYY-MM-DDT%H%M%SZ'")