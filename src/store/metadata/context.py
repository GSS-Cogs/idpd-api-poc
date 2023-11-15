import json
from pathlib import Path


class ContextStore:
    def __init__(self):
        with open(Path("src/store/metadata/context.json").absolute(), "r") as json_file:
            self.context = json.load(json_file)

    def get_context(self):
        return self.context
