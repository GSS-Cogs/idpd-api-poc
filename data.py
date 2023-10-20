"""
Tool that uses jsonld files in /src/store/metadata/stub/content to:

- create ttl files per resource
- create a seed.trig file repredenting single load file of these
  resources as named graphs.
- loads this seed.trig into an oxigraph database running on
  http://localhost:7878

Please run this vai the Makefile if you want to finesses this behaviour.
"""

from ast import List
from ctypes import Union
from dataclasses import Field
from datetime import datetime
from enum import Enum
import json
import os
from os import linesep
from pathlib import Path
import shutil
from pydantic import BaseModel

from pytz import timezone
from rdflib import ConjunctiveGraph, Dataset, BNode, Graph
from rdflib import Literal, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, _node_to_sparql
from rdflib.namespace import DCAT, DCTERMS, FOAF, RDF, XSD

from src import schemas

# TODO - will need updating when the details are worked out.
def set_context(resource_item: dict) -> dict:
    """
    Set a specific context location to inform the RDF created
    from the jsonld samples.
    """
    context_file = Path("src/store/metadata/context.json")

    with open(context_file) as f:
        context = json.load(f)

    resource_item["@context"] = context
    return resource_item

def populate(oxigraph_url=None, write_to_db=True):

    this_dir = Path(__file__).parent
    repo_root = this_dir.parent
    subbed_metadata_store_content_path = Path("src/store/metadata/stub/content"
    ).absolute()

    # Clear up any previous
    out = Path(this_dir / "out")
    if out.exists():
        shutil.rmtree(out.absolute())
    out.mkdir()

    # Conjuctive flavour of graph as in RDF terms each resource
    # is its own invidual named graph of a specific type.
    g = ConjunctiveGraph()

    # Remove then recreate any previous out folder
    out_dir = Path("out")
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir()

    # ------------------
    # Datasets resources
    # ------------------

    # Load from disk
    datasets_source_path = Path(subbed_metadata_store_content_path / "datasets.json")
    with open(datasets_source_path) as f:
        datasets_source_dict = json.load(f)

    # Validate then add to graph
    schemas.Datasets(**datasets_source_dict)
    g = Graph().parse(data=json.dumps(set_context(datasets_source_dict)), format="json-ld")

    # ------------------
    # Editions resources
    # ------------------

    # TODO - need to iterate all files in ./edtions not just the one

    # Load from disk
    editions_source_path = Path(subbed_metadata_store_content_path / "editions/cpih_2022-01.json")
    with open(editions_source_path) as f:
        editions_source_dict = json.load(f)

    # Validate then add to graph
    class ContactPoint(BaseModel):
        name: str
        email: str = Field(pattern=r"^mailto:[\w\.-]+@[\w\.-]+\.\w{2,}$")
    
    class Frequency(Enum):
        triennial = "triennial"
        biennial = "biennial"
        annual = "annual"
        semiannual = "semiannual"
        threeTimesAYear = "three_times_a_year"
        quarterly = "quarterly"
        bimonthly = "bimonthly"
        monthly = "monthly"
        semimonthly = "semimonthly"
        biweekly = "biweekly"
        threeTimesAMonth = "three_times_a_week"
        weekly = "weekly"
        semiweekly = "semiweekly"
        threeTimesAWeek = "three_times_a_week"
        daily = "daily"
        continuous = "continuous"
        irregular = "irregular"
    
    class Column(BaseModel):
        name: str
        datatype: str
        titles: str
        description: str

    class TableSchema(BaseModel):
        columns: list[Column]

    class Edition(BaseModel):
        id: str = Field(alias="@id")
        type: Literal["dcat:Dataset"] = Field(alias="@type")
        in_series: str
        identifier: str
        title: str = Field(max_length=90)
        summary: str = Field(max_length=200)
        description: str = Field(max_length=250)
        publisher: str
        creator: str
        contact_point: ContactPoint
        topics: Union[str, List[str]]
        frequency: Frequency
        keywords: list[str]
        licence: str
        issued: str = Field(
            pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
        )
        modified: str = Field(
            pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
        )
        spatial_coverage: str = Field(pattern=r"^[EJKLMNSW]{1}\d{8}$")
        temporal_coverage: str
        next_release: str = Field(
            pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$",
        )
        versions_url: str
        versions: List
        table_schema: TableSchema

    class Editions(BaseModel):
        context: str = Field(alias="@context")
        id: str = Field(alias="@id")
        type: Literal["hydra:Collection"] = Field(alias="@type")
        title: str = Field(max_length=90)
        editions: List[Edition]


    g += Graph().parse(data=json.dumps(set_context(editions_source_dict)), format="json-ld")

    # ------------------
    # Versions resources
    # ------------------

    # TODO - need to iterate all files in ./editions/versions not just the one
    versions_source_path = Path(subbed_metadata_store_content_path / "editions/versions/cpih_2022-01.json")
    with open(versions_source_path) as f:
        versions_source_dict = json.load(f)

    # Validate then add to graph
    class Column(BaseModel):
        name: str
        datatype: str
        titles: str
        description: str

    class TableSchema(BaseModel):
        columns: list[Column]

    class Version(BaseModel):
        type: List[str] = Field(alias="@type")
        id: str = Field(alias="@id")
        identifier: str
        issued: str = Field(
            pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
        )
        title: str = Field(max_length=90)
        summary: str = Field(max_length=200)
        description: str = Field(max_length=250)
        download_url: str
        media_type: str
        table_schema: TableSchema

    class Versions(BaseModel):
        context: str = Field(alias="@context")
        id: str = Field(alias="@id")
        type: Literal["hydra:Collection"] = Field(alias="@type")
        title: str = Field(max_length=90)
        versions: List[Version]
        count: int
        offset: int


    g += Graph().parse(data=json.dumps(set_context(versions_source_dict)), format="json-ld")

    # ------------------
    # Topics resources
    # ------------------

    topics_source_path = Path(subbed_metadata_store_content_path / "topics.json")
    with open(topics_source_path) as f:
        topics_source_dict = json.load(f)

    # Validate then add to graph
    # TODO - add schema validation
    g += Graph().parse(data=json.dumps(set_context(topics_source_dict)), format="json-ld")

    # --------------------
    # Publishers resources
    # --------------------

    publisher_source_path = Path(subbed_metadata_store_content_path / "publishers.json")
    with open(publisher_source_path) as f:
        topics_source_dict = json.load(f)

    # Validate then add to graph
    # TODO - add schema validation
    g += Graph().parse(data=json.dumps(set_context(topics_source_dict)), format="json-ld")

    out_path = Path("out/seed.ttl")
    g.serialize(out_path, format="ttl")

    if write_to_db:

        assert (
            oxigraph_url
        ), "You need to specfiy the oxigraph url via the OXIGRAPH_URL env var."

        # Now get this seed data into the database
        # adapted from:
        # - https://github.com/rossbowen/poc-api/blob/main/api/src/poc_api/database.py
        # - https://github.com/rossbowen/poc-api/blob/main/api/src/poc_api/seed/seed.py

        def skolemise(node):
            if isinstance(node, BNode):
                return "<bnode:b%s>" % node
            return _node_to_sparql(node)

        configuration = (f"{oxigraph_url}/query", f"{oxigraph_url}/update")
        db = Dataset(store=SPARQLUpdateStore(*configuration, node_to_sparql=skolemise))
        db.parse(out_path)


if __name__ == "__main__":
    oxigraph_url = os.getenv("GRAPH_DB_URL", None)
    populate(oxigraph_url=oxigraph_url)
