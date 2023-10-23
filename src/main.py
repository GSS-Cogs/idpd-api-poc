import os
from typing import Optional

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

from constants import CSV, JSONLD
import schemas
from store import OxigraphMetadataStore, StubCsvStore, StubMetadataStore

# Simple env var flag to allow local browsing of api responses
# while developing.
BROWSABLE = os.environ.get("LOCAL_BROWSE_API")

# Create a FastAPI instance with metadata
app = FastAPI(
    title="IDPD-API-POC",
    description="A proof of concept API layer to manage content negotiation across IDPD resources and provide an abstraction to 3rd party data services. This API provides access to various metadata, including datasets, editions, publishers, and topics.",
    version="0.0.1",
)


@app.get(
    "/datasets", 
    response_model=Optional[schemas.Datasets], 
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response. Returns a list of datasets.",
            "model": schemas.Datasets,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found. No datasets found.",
            "model": None,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported.",
            "model": None,
        },
    }
)
def get_all_datasets(
    request: Request,
    response: Response,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    """
    Retrieve all the datasets.
    This endpoint returns information on datasets available in the system.
    
    """
        
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        datasets = metadata_store.get_datasets()
        if datasets is not None:
            response.status_code = status.HTTP_200_OK
            return datasets
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/datasets/{dataset_id}", 
        response_model=Optional[schemas.Dataset],
        responses={
            status.HTTP_200_OK: {
                "description": "Successful response. Returns detailed information about the dataset.",
                "model": schemas.Dataset,
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Not Found. The dataset with the given ID is not found.",
                "model": None,
            },
            status.HTTP_406_NOT_ACCEPTABLE: {
                "description": "Not Acceptable. The requested format is not supported.",
                "model": None,
            }
        }
)
def get_dataset_by_id(
    request: Request,
    response: Response,
    dataset_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    """
    Retrieve information about a specific dataset by ID.
    This endpoint returns detailed information about a dataset based on its unique identifier.

    """
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        dataset = metadata_store.get_dataset(dataset_id)
        if dataset is not None:
            response.status_code = status.HTTP_200_OK
            return dataset
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/datasets/{dataset_id}/editions",
        response_model=Optional[schemas.Editions],
        responses={
            status.HTTP_200_OK: {
                "description": "Successful response. Returns all the editions for the dataset.",
                "model": schemas.Edition,
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Not Found. No editions are found for the dataset.",
                "model": None,
            },
            status.HTTP_406_NOT_ACCEPTABLE: {
                "description": "Not Acceptable. The requested format is not supported.",
                "model": None,
            }
        }
)
def get_dataset_editions(
    request: Request,
    response: Response,
    dataset_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    """
    Retrieve all the editions for a specific dataset.
    This endpoint returns all the editions associated with a particular dataset.

    """
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        editions = metadata_store.get_editions(dataset_id)
        if editions is not None:
            response.status_code = status.HTTP_200_OK
            return editions
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/datasets/{dataset_id}/editions/{edition_id}",
         response_model=Optional[schemas.Edition],
        responses={
            status.HTTP_200_OK: {
                "description": "Successful response. Returns detailed information about the edition.",
                "model":schemas.Edition,
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Not Found. The edition with the given ID is not found.",
                "model": None,
            },
            status.HTTP_406_NOT_ACCEPTABLE: {
                "description": "Not Acceptable. The requested format is not supported.",
                "model": None,
            }
        }
)
def get_dataset_edition_by_id(
    request: Request,
    response: Response,
    dataset_id: str,
    edition_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    """
    Retrieve information about a specific edition of a dataset.
    This endpoint returns detailed information about a specific edition of a dataset.
    
    """
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        edition = metadata_store.get_edition(dataset_id, edition_id)
        if edition is not None:
            response.status_code = status.HTTP_200_OK
            return edition
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/datasets/{dataset_id}/editions/{edition_id}/versions",  response_model=Optional[schemas.Versions])
def versions(
    request: Request,
    response: Response,
    dataset_id: str,
    edition_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        versions = metadata_store.get_versions(dataset_id, edition_id)
        if versions is not None:
            response.status_code = status.HTTP_200_OK
            return versions
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}", response_model=Optional[schemas.Version])
def version(
    request: Request,
    response: Response,
    dataset_id: str,
    edition_id: str,
    version_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
    csv_store: StubCsvStore = Depends(StubCsvStore)
):
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        version = metadata_store.get_version(dataset_id, edition_id, version_id)
        if version is not None:
            response.status_code = status.HTTP_200_OK
            return version
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    elif request.headers["Accept"] == CSV:
        csv_data = csv_store.get_version(dataset_id, edition_id, version_id)
        if csv_data is not None:
            response.status_code = status.HTTP_200_OK
            return csv_data
        else:
            response.status_code = status.HTTP_404_NOT_FOUND
            return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/publishers",
        responses={
            status.HTTP_200_OK: {
                "description": "Successful response. Returns all the publishers available in the system.",
                "model": "",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Not Found. No publishers are found.",
                "model": None,
            },
            status.HTTP_406_NOT_ACCEPTABLE: {
                "description": "Not Acceptable. The requested format is not supported.",
                "model": None,
            }
        }
)
def get_all_publishers(
    request: Request,
    response: Response,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    """
    Retrieve all the publishers.
    This endpoint returns all the publishers available in the system.
 
    """
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        publishers = metadata_store.get_publishers()
        if publishers is not None:
            response.status_code = status.HTTP_200_OK
            return publishers
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/publishers/{publisher_id}",
        responses={
            status.HTTP_200_OK: {
                "description": "Successful response. Returns detailed information about the publisher.",
                "model": "",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Not Found. The publisher with the given ID is not found.",
                "model": None,
            },
            status.HTTP_406_NOT_ACCEPTABLE: {
                "description": "Not Acceptable. The requested format is not supported.",
                "model": None,
            }
        }
)
def get_publisher_by_id(
    request: Request,
    response: Response,
    publisher_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    """
    Retrieve information about a specific publisher by ID.
    This endpoint returns detailed information about a specific publisher based on its unique identifier.
    
    """
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        publisher = metadata_store.get_publisher(publisher_id)
        if publisher is not None:
            response.status_code = status.HTTP_200_OK
            return publisher
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/topics", 
        responses={
            status.HTTP_200_OK: {
                "description": "Successful response. Returns all of the topics available in the system.",
                "model": "",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Not Found. No topics are found.",
                "model": None,
            },
            status.HTTP_406_NOT_ACCEPTABLE: {
                "description": "Not Acceptable. The requested format is not supported.",
                "model": None,
            }
        }
)
def get_all_topics(
    request: Request,
    response: Response,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    """
    Retrieve all the topics.
    This endpoint returns all of the topics available in the system.
    
    """
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        topics = metadata_store.get_topics()
        if topics is not None:
            response.status_code = status.HTTP_200_OK
            return topics
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/topics/{topic_id}", 
        responses={
            status.HTTP_200_OK: {
                "description": "Successful response. Returns detailed information about the topic.",
                "model": "",
            },
            status.HTTP_404_NOT_FOUND: {
                "description": "Not Found. The topic with the given ID is not found.",
                "model": None,
            },
            status.HTTP_406_NOT_ACCEPTABLE: {
                "description": "Not Acceptable. The requested format is not supported.",
                "model": None,
            }
        }
)
def get_topic_by_id(
    request: Request,
    response: Response,
    topic_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    """
    Retrieve information about a specific topic by ID.
    This endpoint returns detailed information about a specific topic based on its unique identifier.

    """
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        topic = metadata_store.get_topic(topic_id)
        if topic is not None:
            response.status_code = status.HTTP_200_OK
            return topic
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


# note: download only for now, needs expanding
@app.get("/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}",
        responses={
            status.HTTP_200_OK: {
                "description": "Successful response. Returns the CSV data for the specified version.",
                "media_type": "text/csv",
            },           
            status.HTTP_404_NOT_FOUND: {
                "description": "Not Found.",
            }
        }
)
def get_dataset_edition_version_by_id(
    request: Request,
    response: Response,
    dataset_id: str,
    edition_id: str,
    version_id: str,
    csv_store: StubCsvStore = Depends(StubCsvStore),
):
    """
    Retrieve a specific version and edition of a dataset.
    This endpoint allows downloading a specific version of a dataset in CSV format.

    """
    csv_data = csv_store.get_version(dataset_id, edition_id, version_id)
    if csv_data is not None:
        response.status_code = status.HTTP_200_OK
        return csv_data
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
