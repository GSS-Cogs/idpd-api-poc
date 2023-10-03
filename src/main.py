import os
from typing import List, Optional

from fastapi import FastAPI, Request, Response, status

from constants import JSONLD
from store import StubCsvStore, StubMetadataStore

import schemas

# Simple env var flag to allow local browsing of api responses
# while developing.
BROWSABLE = os.environ.get("LOCAL_BROWSE_API")

# Mapping specific store implementations to specific endpoints.
# This is an interim measure to allow us to stub out endpoints
# and target implement them one at a time.
stub_metadata_store = StubMetadataStore()
stub_csv_store = StubCsvStore()

app = FastAPI()
app.state.stores = {
    "datasets_metadata": stub_metadata_store,
    "dataset_metadata": stub_metadata_store,
    "topics_metadata": stub_metadata_store,
    "topic_metadata": stub_metadata_store,
    "publishers_metadata": stub_metadata_store,
    "publisher_metadata": stub_metadata_store,
    "version_csv": stub_csv_store,
}


@app.get("/datasets", response_model=Optional[schemas.Datasets])
def datasets(request: Request, response: Response):
    metadata_store = app.state.stores["datasets_metadata"]
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        return metadata_store.get_datasets()
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/datasets/{id}")
def dataset(
    request: Request,
    response: Response,
    id: str,
    response_model=Optional[schemas.Dataset],
):
    metadata_store = app.state.stores["dataset_metadata"]
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        dataset = metadata_store.get_dataset(id)
        if dataset is not None:
            response.status_code = status.HTTP_200_OK
            return dataset
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/publishers")
def publishers(request: Request, response: Response):
    metadata_store = app.state.stores["publishers_metadata"]
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        return metadata_store.get_publishers()
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/publishers/{id}")
def publisher(request: Request, response: Response, id: str):
    metadata_store = app.state.stores["publisher_metadata"]
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        publisher = metadata_store.get_publisher(id)
        if publisher is not None:
            response.status_code = status.HTTP_200_OK
            return publisher
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/topics")
def topics(request: Request, response: Response):
    metadata_store = app.state.stores["topics_metadata"]
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        return metadata_store.get_topics()
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/topics/{id}")
def topic(request: Request, response: Response, id: str):
    metadata_store = app.state.stores["topic_metadata"]
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        topic = metadata_store.get_topic(id)
        if topic is not None:
            response.status_code = status.HTTP_200_OK
            return topic
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


# note: download only for now, needs expanding
@app.get("/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}")
def version(
    request: Request,
    response: Response,
    dataset_id: str,
    edition_id: str,
    version_id: str,
):
    csv_store = app.state.stores["version_csv"]
    data = csv_store.get_version(dataset_id, edition_id, version_id)
    if data is not None:
        response.status_code = status.HTTP_200_OK
        return data
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
