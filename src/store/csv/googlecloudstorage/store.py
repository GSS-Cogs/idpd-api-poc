from typing import AsyncGenerator, Tuple

import aiohttp
import httpx
from fastapi import HTTPException

from custom_logging import logger

from ..base import BaseCsvStore


async def _file_stream(file_url: str):
    """
    Generator function to stream a csv response in
    managable chunks.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            while chunk := await response.content.read(1024):
                yield chunk


def _download_exists(download_url: str):
    """
    Helper to make sure a csv download url exists before we try
    and download it from GCP
    """
    with httpx.Client() as client:
        try:
            # Send a HEAD request to check if the object exists
            response = client.head(download_url)

            # If the response status code is not 200 (OK), log out
            # the problem and False
            if response.status_code != 200:
                logger.error(
                    "Unable to get download url",
                    data={"download_url": download_url},
                    error=[
                        HTTPException(
                            f"Failed to get {download_url} with status code {response.status_code}"
                        )
                    ],
                )
                return False
            else:
                return True
        # If any other errors are encountered do the same
        except Exception as err:
            logger.error(
                "Unable to download url",
                data={"download_url": download_url},
                error=[err],
            )
            return False


class CloudStorageCsvStore(BaseCsvStore):
    """
    Returns the requested csv from a PUBLIC google
    storage bucket.
    """

    def setup(self):
        self.bucket_base_path = "https://storage.googleapis.com/idpd-poc-api"

    def get_version(
        self, dataset_id: str, edition_id: str, version_id: str, check_exists=True
    ) -> Tuple[str, AsyncGenerator[bytes, None]]:
        """
        Provides a filename and async download generator as a Tuple.
        Also uses an options request to check the file in question
        exists on GCP beforehand.

        The check_exists kwarg can be used to toggle this
        check off (for test purposes primarily).
        """
        file_path = f"{dataset_id}/{edition_id}/{version_id}"
        if not file_path.endswith(".csv"):
            file_path = file_path + ".csv"

        download_url = f"{self.bucket_base_path}/{file_path}"

        logging_data = (
            {
                "dataset_id": dataset_id,
                "edition_id": edition_id,
                "version_id": version_id,
                "combined_file_path": file_path,
                "url": download_url,
            },
        )

        logger.info("Received request for csv", data=logging_data)

        if check_exists:
            if not _download_exists(download_url):
                return None, None

        filename_for_download = f"{dataset_id}_{edition_id}_{version_id}.csv"
        file_stream = _file_stream(download_url)

        return (filename_for_download, file_stream)
