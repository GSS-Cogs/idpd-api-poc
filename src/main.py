import csv
import os

from pathlib import Path
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import FileResponse

from constants import JSONLD
from store import StubStore, StubCsvStore

# Simple env var flag to allow local browsing of api responses
# while developing.
BROWSABLE = os.environ.get("LOCAL_BROWSE_API")

# Mapping specific store implementations to specific endpoints.
# This is an interim measure to allow us to stub out endpoints
# and target implement them one at a time.
stub_metadata_store = StubStore()
stub_csv_store = StubCsvStore()
app = FastAPI()
app.state.stores = {
    "datasets_metadata": stub_metadata_store,
    "dataset_metadata": stub_metadata_store,
    "themes_metadata": stub_metadata_store,
    "theme_metadata": stub_metadata_store,
    "publishers_metadata": stub_metadata_store,
    "publisher_metadata": stub_metadata_store,
    "dataset_csv": stub_csv_store
}


@app.get("/datasets")
def datasets(request: Request, response: Response):
    metadata_store = app.state.stores["datasets_metadata"]
    if request.headers['Accept'] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        return metadata_store.get_datasets()
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return

@app.get("/datasets/{id}")
def dataset_by_id(request: Request, response: Response, id: str):
    metadata_store = app.state.stores["dataset_metadata"]
    if request.headers['Accept'] == JSONLD or BROWSABLE:
        datasets = metadata_store.get_dataset_by_id(id)
        if len(datasets) == 1:
            response.status_code = status.HTTP_200_OK
            return datasets[0]
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return
    
@app.get("/publishers")
def publishers(request: Request, response: Response):
    metadata_store = app.state.stores["publishers_metadata"]
    if request.headers['Accept'] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        return metadata_store.get_publishers()
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return

@app.get("/publishers/{id}")
def publisher_by_id(request: Request, response: Response, id: str):
    metadata_store = app.state.stores["publisher_metadata"]
    if request.headers['Accept'] == JSONLD or BROWSABLE:
        publishers = metadata_store.get_publisher_by_id(id)
        if len(publishers) == 1:
            response.status_code = status.HTTP_200_OK
            return publishers[0]
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return
    
@app.get("/topics")
def topics(request: Request, response: Response):
    metadata_store = app.state.stores["topics_metadata"]
    if request.headers['Accept'] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        return metadata_store.get_topics()
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return

@app.get("/topics/{id}")
def topic_by_id(request: Request, response: Response, id: str):
    metadata_store = app.state.stores["topic_metadata"]
    if request.headers['Accept'] == JSONLD or BROWSABLE:
        themes = metadata_store.get_topic_by_id(id)
        if len(themes) == 1:
            response.status_code = status.HTTP_200_OK
            return themes[0]
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


"""not for included in pr, but to include in prdescrition"""
@app.get("/csv/{id}", response_class=FileResponse)
def get_csv(id: str):
    #data = csv_store.get_csv(id)
    #csv_store = app.state.stores["dataset_csv"]
    the_id =os.getcwd() + "/src//store/stub/csv/" + id
    the_file_path = Path(the_id + ".csv")
    return FileResponse(the_file_path)
