import os
from typing import Optional

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

import schemas
from constants import CSV, JSONLD
from custom_logging import logger
from middleware import logging_middleware
from store import CloudStorageCsvStore, ContextStore, StubMetadataStore

# Simple env var flag to allow local browsing of api responses
# while developing.
BROWSABLE = os.environ.get("LOCAL_BROWSE_API")

# Create a FastAPI instance with metadata
app = FastAPI(
    title="IDPD-API-POC",
    description="A proof of concept API layer to manage content negotiation across IDPD resources and provide an abstraction to 3rd party data services. This API provides access to various metadata, including datasets, editions, publishers, and topics.",
    version="0.0.1",
)

# Add the logging middleware to the app
app.middleware("http")(logging_middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.idpd(\.onsdigital)?\.uk",
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get(
    "/ns",
    responses={
        status.HTTP_200_OK: {"description": "Successful response. Returns a context."},
        status.HTTP_404_NOT_FOUND: {"description": "Not Found. No context found."},
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported."
        },
    },
)
def get_context(
    request: Request,
    response: Response,
    context_store: ContextStore = Depends(ContextStore),
):
    """
    Retrieve the context.
    This endpoint returns information on the context.
    """

    logger.info("Received request for context")
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        context = context_store.get_context()
        if context is not None:
            response.status_code = status.HTTP_200_OK
            return context
        response.status_code = status.HTTP_404_NOT_FOUND
        logger.error("Context not found")
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


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
    },
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

    logger.info("Received request for datasets")

    if request.headers["Accept"] == JSONLD or BROWSABLE:
        datasets = metadata_store.get_datasets()
        if datasets is not None:
            response.status_code = status.HTTP_200_OK
            return datasets
        response.status_code = status.HTTP_404_NOT_FOUND
        logger.error("Datasets not found")
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get(
    "/datasets/{dataset_id}",
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
        },
    },
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
    logger.info("Received request for dataset with ID", data={"dataset_id": dataset_id})

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


@app.get(
    "/datasets/{dataset_id}/editions",
    response_model=Optional[schemas.Editions],
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response. Returns all the editions for the dataset.",
            "model": schemas.Editions,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found. No editions are found for the dataset.",
            "model": None,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported.",
            "model": None,
        },
    },
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
    logger.info(
        "Received request for dataset editions", data={"dataset_id": dataset_id}
    )

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


@app.get(
    "/datasets/{dataset_id}/editions/{edition_id}",
    response_model=Optional[schemas.Edition],
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response. Returns detailed information about the edition.",
            "model": schemas.Edition,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found. The edition with the given ID is not found.",
            "model": None,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported.",
            "model": None,
        },
    },
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
    logger.info(
        "Received request for dataset and edition",
        data={"dataset_id": dataset_id, "edition_id": edition_id},
    )

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


@app.get(
    "/datasets/{dataset_id}/editions/{edition_id}/versions",
    response_model=Optional[schemas.Versions],
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response. Returns all the versions for the specified edition of a dataset.",
            "model": schemas.Versions,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found. No versions are found for the specified edition of the dataset.",
            "model": None,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported.",
            "model": None,
        },
    },
)
def get_dataset_edition_versions(
    request: Request,
    response: Response,
    dataset_id: str,
    edition_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    """
    Retrieve all the versions for a specific edition of a dataset.
    This endpoint returns all the versions associated with a particular edition of a dataset.
    """
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


@app.get(
    "/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}",
    response_model=Optional[schemas.Version],
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response. Returns detailed information about the specified version of a dataset.",
            "model": schemas.Version,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found. The specified version of the dataset is not found.",
            "model": None,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported.",
            "model": None,
        },
    },
)
def get_dataset_edition_version_by_id(
    request: Request,
    response: Response,
    dataset_id: str,
    edition_id: str,
    version_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
    csv_store: CloudStorageCsvStore = Depends(CloudStorageCsvStore),
):
    """
    Retrieve information about a specific version of a dataset.
    This endpoint returns detailed information about a specific version of a dataset based on its unique identifier.
    """

    if request.headers["Accept"] == CSV:
        csv_file_name, data_stream = csv_store.get_version(
            dataset_id, edition_id, version_id
        )
        if None in [csv_file_name, data_stream]:
            response.status_code = status.HTTP_404_NOT_FOUND
            return
        response = StreamingResponse(data_stream, media_type="application/octet-stream")
        response.headers[
            "Content-Disposition"
        ] = f'attachment; filename="{csv_file_name}"'
        response.status_code = status.HTTP_200_OK
        return response

    elif request.headers["Accept"] == JSONLD or BROWSABLE:
        version = metadata_store.get_version(dataset_id, edition_id, version_id)
        if version is not None:
            response.status_code = status.HTTP_200_OK
            return version
        response.status_code = status.HTTP_404_NOT_FOUND
        return

    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get(
    "/publishers",
    response_model=Optional[schemas.Publishers],
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response. Returns all the publishers available in the system.",
            "model": schemas.Publishers,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found. No publishers are found.",
            "model": None,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported.",
            "model": None,
        },
    },
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
    logger.info("Received request for publishers", data={"request_type": "publishers"})

    if request.headers["Accept"] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        publishers = metadata_store.get_publishers()
        if publishers is not None:
            response.status_code = status.HTTP_200_OK
            return publishers
        response.status_code = status.HTTP_404_NOT_FOUND
        logger.error("Publishers not found")
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get(
    "/publishers/{publisher_id}",
    response_model=Optional[schemas.Publisher],
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response. Returns detailed information about the publisher.",
            "model": schemas.Publisher,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found. The publisher with the given ID is not found.",
            "model": None,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported.",
            "model": None,
        },
    },
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
    logger.info(
        "Received request for publisher with ID", data={"publisher_id": publisher_id}
    )

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


@app.get(
    "/topics",
    response_model=Optional[schemas.Topics],
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response. Returns all of the topics available in the system.",
            "model": schemas.Topics,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found. No topics are found.",
            "model": None,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported.",
            "model": None,
        },
    },
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
    logger.info("Received request for topics", data={"request_type": "topics"})

    if request.headers["Accept"] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        topics = metadata_store.get_topics()
        if topics is not None:
            response.status_code = status.HTTP_200_OK
            return topics
        response.status_code = status.HTTP_404_NOT_FOUND
        logger.error("Topics not found")
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get(
    "/topics/{topic_id}",
    response_model=Optional[schemas.Topic],
    responses={
        status.HTTP_200_OK: {
            "description": "Successful response. Returns detailed information about the topic.",
            "model": schemas.Topic,
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found. The topic with the given ID is not found.",
            "model": None,
        },
        status.HTTP_406_NOT_ACCEPTABLE: {
            "description": "Not Acceptable. The requested format is not supported.",
            "model": None,
        },
    },
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
    logger.info("Received request for topic with ID", data={"topic_id": topic_id})

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
