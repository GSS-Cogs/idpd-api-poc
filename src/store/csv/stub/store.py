from pathlib import Path

from fastapi.responses import FileResponse

from ..base import BaseCsvStore


class StubCsvStore(BaseCsvStore):
    """
    A stub of a store that returns representative csv from
    files stored on disk.
    """

    def setup(self):
        self.datasets = {}

        content_dir = Path(Path(__file__).parent / "content")
        self.datasets["cpih/2022-01/1"] = Path(
            content_dir / "cpih/2022-1/1.csv"
        ).absolute()

    def get_version(self, dataset_id: str, edition_id: str, version_id: str):
        csv_identifier = f"{dataset_id}/{edition_id}/{version_id}"
        csv_path = self.datasets.get(csv_identifier, None)
        return FileResponse(csv_path) if csv_path else None
