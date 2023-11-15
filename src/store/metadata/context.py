import json
from pathlib import Path


class ContextStore:
    def __init__(self):
        this_dir = Path(__file__).parent
        with open(Path(this_dir / "context.json").absolute(), "r") as json_file:
            self.context = json.load(json_file)

    def get_context(self):
        return self.context
