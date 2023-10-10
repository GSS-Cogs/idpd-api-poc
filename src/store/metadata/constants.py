# Note: differentiating between "data_constants" and "constants"
# as this file is likely to get quite complicated.

from pathlib import Path
import json

this_dir = Path(__file__).parent

with open(this_dir / "context.json") as f:
    CONTEXT = json.load(f)
