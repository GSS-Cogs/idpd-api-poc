import glob
from pathlib import Path

from fastapi.responses import FileResponse

from custom_logging import logger

from ..base import BaseCsvStore


class StubCsvStore(BaseCsvStore):
    """
    A stub of a store that returns representative csv from
    files stored on disk.
    """

    def setup(self):
        self.datasets = {}

        content_dir = Path(Path(__file__).parent / "content").absolute()
        csv_file_paths = glob.glob(f"{content_dir}/**/**/*.csv", recursive=True)

        # set as glob'ing multiple wildcard dirs can result in multiple hits for a single file
        for csv_file_path in set(csv_file_paths):
            # Create a key of dataset_id/edition_id/verion_id
            csv_key = "/".join(csv_file_path.split("/")[-3:]).rstrip(".csv")

            # Now add to dict so we can find them when a user requests
            self.datasets[csv_key] = csv_file_path

    def get_version(self, dataset_id: str, edition_id: str, version_id: str):
        # Use variables to create the unique custom identifier for the csv
        # being requested.
        csv_identifier = f"{dataset_id}/{edition_id}/{version_id}".rstrip(".csv")
        logger.info(
            "Recieved request for csv",
            data={
                "dataset_id": dataset_id,
                "edition_id": edition_id,
                "version_id": version_id,
                "combined_csv_id": csv_identifier,
            },
        )

        # Try and get it, then log out whether or not we did.
        csv_path = self.datasets.get(csv_identifier, None)
        logger.info(
            "Acquiring csv from stub store",
            data={
                "combined_csv_id": csv_identifier,
                "csv_ids_in_store": list(self.datasets.keys()),
                "csv_acquired": False if csv_path is None else True,
            },
        )

        return FileResponse(csv_path) if csv_path else None
