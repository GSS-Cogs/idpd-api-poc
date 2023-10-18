import logging
import os
from typing import Optional

from fastapi import Depends, FastAPI, Request, Response, status
import structlog

from constants import JSONLD
import schemas
from store import StubCsvStore, StubMetadataStore

from custom_logging import configure_logger, logger
from structlog.contextvars import bind_contextvars, clear_contextvars
import time
# Simple env var flag to allow local browsing of api responses
# while developing.
BROWSABLE = os.environ.get("LOCAL_BROWSE_API")

app = FastAPI()
configure_logger()


@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    clear_contextvars()
    # These context vars will be added to all log entries emitted during the request
    request_id = request.headers.get("request-id")
    bind_contextvars(request_id=request_id)

    start_time = time.perf_counter_ns()

    try:
        response = await call_next(request)
    except Exception as exc:
        response = Response(status_code=500)
        structlog.get_logger("api.error").exception("Uncaught exception", exc_info=exc)
        raise
    finally:
        process_time = time.perf_counter_ns() - start_time
        status_code = response.status_code

    log_message = "Request completed"
    log_context = {
        "path": request.url.path,
        "method": request.method,
        "status_code": status_code,
        "process_time": process_time / 10 ** 9,  # Convert to seconds
    }

    if status_code == 200:
        logger.info(log_message, **log_context)
    elif status_code == 404:
        log_message = "Resource not found"
        logger.info(log_message, **log_context)
    elif status_code == 406:
        log_message = "Request not acceptable"
        logger.error(log_message, **log_context)


        response.headers["X-Process-Time"] = str(process_time / 10 ** 9)

    return response
    
@app.get("/datasets", response_model=Optional[schemas.Datasets])
async def datasets(
    request: Request,
    response: Response,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    logger.info("Received request for datasets")
       
    if request.headers["Accept"] == JSONLD or BROWSABLE:
        response.status_code = status.HTTP_200_OK
        datasets = metadata_store.get_datasets()
        if datasets is not None:
            response.status_code = status.HTTP_200_OK
            return datasets
        response.status_code = status.HTTP_404_NOT_FOUND
        return
    else:
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
        return


@app.get("/datasets/{dataset_id}", response_model=Optional[schemas.Dataset])
def dataset(
    request: Request,
    response: Response,
    dataset_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    logger.info(f"Received request for dataset with ID: {dataset_id}", dataset_id)
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


@app.get("/datasets/{dataset_id}/editions")
def editions(
    request: Request,
    response: Response,
    dataset_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    logger.info(f"Received request for dataset (ID: {dataset_id}) editions.")
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


@app.get("/datasets/{dataset_id}/editions/{edition_id}")
def edition(
    request: Request,
    response: Response,
    dataset_id: str,
    edition_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    logger.info(f"Received request for dataset (ID: {dataset_id}) and edition (ID: {edition_id}).")
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


@app.get("/publishers")
def publishers(
    request: Request,
    response: Response,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    logger.info("Received request for publishers")
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


@app.get("/publishers/{publisher_id}")
def publisher(
    request: Request,
    response: Response,
    publisher_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    logger.info(f"Received request for publisher with ID: {publisher_id}", publisher_id)
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


@app.get("/topics")
def topics(
    request: Request,
    response: Response,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    logger.info("Received request for publishers")
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


@app.get("/topics/{topic_id}")
def topic(
    request: Request,
    response: Response,
    topic_id: str,
    metadata_store: StubMetadataStore = Depends(StubMetadataStore),
):
    logger.info(f"Received request for topic with ID: {topic_id}", topic_id)
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
@app.get("/datasets/{dataset_id}/editions/{edition_id}/versions/{version_id}")
def version(
    request: Request,
    response: Response,
    dataset_id: str,
    edition_id: str,
    version_id: str,
    csv_store: StubCsvStore = Depends(StubCsvStore),
):
    logger.info(f"Received request for dataset (ID: {dataset_id}), edition (ID: {edition_id}), and version (ID: {version_id}).")
    csv_data = csv_store.get_version(dataset_id, edition_id, version_id)
    if csv_data is not None:
        response.status_code = status.HTTP_200_OK
        return csv_data
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return
