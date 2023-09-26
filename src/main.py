from fastapi import FastAPI, Request, Response, status

from constants import JSONLD
from store import StubStore


# Mapping specific store implementations to specific endpoints.
# This is an interim measure to allow us to stub out endpoints
# and target implement them one at a time.
stub_metadata_store = StubStore()
stores = {
    "datasets_metadata": stub_metadata_store,
    "dataset_metadata": stub_metadata_store,
    "themes_metadata": stub_metadata_store,
    "theme_metadata": stub_metadata_store,
    "publishers_metadata": stub_metadata_store,
    "publisher_metadata": stub_metadata_store
}

app = FastAPI()

@app.get("/datasets")
def datasets(request: Request, response: Response):
    metadata_store = stores["datasets_metadata"]
    if request.headers['Accept'] == JSONLD:
        response.status_code = status.HTTP_200_OK
        return metadata_store.get_datasets()
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return

@app.get("/datasets/<id>")
def datasets(request: Request, response: Response, id: str):
    metadata_store = stores["dataset_metadata"]
    if request.headers['Accept'] == JSONLD:
        datasets = metadata_store.get_dataset_by_id(id)
        if len(datasets) == 1:
            response.status_code = status.HTTP_200_OK
            return datasets[0]
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return
    
@app.get("/publishers")
def datasets(request: Request, response: Response):
    metadata_store = stores["publishers_metadata"]
    if request.headers['Accept'] == JSONLD:
        response.status_code = status.HTTP_200_OK
        return metadata_store.get_publishers()
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return

@app.get("/publishers/<id>")
def datasets(request: Request, response: Response, id: str):
    metadata_store = stores["publisher_metadata"]
    if request.headers['Accept'] == JSONLD:
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
def datasets(request: Request, response: Response):
    metadata_store = stores["topics_metadata"]
    if request.headers['Accept'] == JSONLD:
        response.status_code = status.HTTP_200_OK
        return metadata_store.get_topics()
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return

@app.get("/topics/<id>")
def datasets(request: Request, response: Response, id: str):
    metadata_store = stores["topic_metadata"]
    if request.headers['Accept'] == JSONLD:
        themes = metadata_store.get_topic_by_id(id)
        if len(themes) == 1:
            response.status_code = status.HTTP_200_OK
            return themes[0]
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return