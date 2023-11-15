# Note: differentiating between "data_constants" and "constants"
# as this file is likely to get quite complicated.

import json
from pathlib import Path

this_dir = Path(__file__).parent

with open(this_dir / "context.json") as f:
    CONTEXT = json.load(f)
