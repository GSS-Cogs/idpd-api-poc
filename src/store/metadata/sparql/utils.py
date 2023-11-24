from enum import Enum
from pathlib import Path
from typing import Dict, Optional

from rdflib import Graph
from rdflib.term import Identifier

from store.metadata.sparql.queries import sparql_queries

APP_ROOT_DIR_PATH = Path(__file__).parent.parent.resolve()


class SPARQLQueryName(Enum):
    CONSTRUCT_DATASETS = sparql_queries["datasets"]
    CONSTRUCT_DATASET = sparql_queries["dataset"]
    CONSTRUCT_KEYWORDS = sparql_queries["keywords"]
    CONSTRUCT_TOPICS = sparql_queries["topics"]
    CONSTRUCT_CONTACT_POINT = sparql_queries["contact_point"]
    CONSTRUCT_TEMPORAL_COVERAGE = sparql_queries["temporal_coverage"]
    CONSTRUCT_EDITIONS = sparql_queries["editions"]


def get_query_string_from_file(query_type: SPARQLQueryName) -> str:
    file_path: Path = (
        APP_ROOT_DIR_PATH / "sparql" / "queries" / (query_type.value + ".sparql")
    )

    try:
        with open(
            file_path,
            "r",
        ) as f:
            return f.read()
    except Exception as ex:
        raise Exception(sparql_file_path=file_path.absolute()) from ex


def construct(
    query: str, graph: Graph, init_bindings: Optional[Dict[str, Identifier]] = None
) -> Graph:
    return graph.query(query, initBindings=init_bindings).graph
