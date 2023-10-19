from logging import exception
from pathlib import Path
from google.cloud import storage

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

class CloudStorageCsvStore(BaseCsvStore):
    """
    stub of a google clouds storage(bucket)
    that returns a csvfile
    """

    #create the client in setup
    def setup(self):
        pass
    
    def get_version(self, dataset_id: str, edition_id: str, version_id: str):
        client = storage.Client.create_anonymous_client()
        bucket = client.lookup_bucket("idpd-poc-api")
        file_path = f"{dataset_id}/{edition_id}/{version_id}"
        if not file_path.endswith(".csv"):
            file_path = file_path + ".csv"
        blop = bucket.blob(file_path)
        the_url = f"gs://idpd-poc-api/{blop.name}/{file_path}"
        #the_url = f"https://storage.googleapis.com/idpd-poc-api/{blop.name}/{file_path}"
        return FileResponse(the_url)
        #if the_url else None
        #blop.download_to_filename("src/store/csv/stub/1.csv")
