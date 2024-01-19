import json
from pathlib import Path
from typing import Optional

from custom_logging import configure_logger, logger

configure_logger()

class ContextStore:
    def __init__(self):
        this_dir = Path(__file__).parent
        with open(Path(this_dir / "context.json").absolute(), "r") as json_file:
            self.context = json.load(json_file)

    def get_context(self, request_id: Optional[str] = None):
        logger.info("Getting Context", request_id=request_id)
        return self.context
    
