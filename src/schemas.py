"""
This module defines the pydantic models for the API. The schemas are used to
validate the structure of the data returned by the API.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Literal, Optional, Union, List


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


class ContactPoint(BaseModel):
    name: str
    email: str = Field(pattern=r"^mailto:[\w\.-]+@[\w\.-]+\.\w{2,}$")


class PeriodOfTime(BaseModel):
    start: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$",
    )
    end: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$",
    )


class Column(BaseModel):
    name: str
    datatype: str
    titles: str
    description: str


class TableSchema(BaseModel):
    columns: list[Column]


class Distribution(BaseModel):
    id: str = Field(alias="@id")
    type: List[str] = Field(alias="@type")
    media_type: str
    table_schema: TableSchema

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


class SummarisedEdition(BaseModel):
    """
    A short form schema for Edition as presented
    at the /datasets level
    """
    id: str = Field(alias="@id")
    issued: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
    )
    modified: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
    )

class Editions(BaseModel):
    context: str = Field(alias="@context")
    id: str = Field(alias="@id")
    type: Literal["hydra:Collection"] = Field(alias="@type")
    title: str = Field(max_length=90)
    editions: List[Edition]


# If we wanted to provide the ability to attach arbitrary RDF we might want to
# look at https://github.com/pydantic/pydantic/discussions/5853
class Dataset(BaseModel):
    #context: Optional[str] = Field(alias="@context")
    id: str = Field(alias="@id")
    type: Literal["dcat:DatasetSeries"] = Field(alias="@type")
    identifier: str
    title: str = Field(max_length=90)
    summary: str = Field(max_length=200)
    description: str = Field(max_length=250)
    issued: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
    )
    modified: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$"
    )
    next_release: str = Field(
        pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})?$",
    )
    publisher: str
    creator: str
    contact_point: ContactPoint
    topics: Union[str, List[str]]
    frequency: Frequency
    keywords: list[str]
    licence: str
    spatial_coverage: str = Field(pattern=r"^[EJKLMNSW]{1}\d{8}$")
    temporal_coverage: PeriodOfTime
    editions: List[Union[Edition, SummarisedEdition]]
    editions_url: str

class Datasets(BaseModel):
    context: str = Field(alias="@context")
    id: str = Field(alias="@id")
    type: List[str] = Field(alias="@type")
    title: str = Field(max_length=90)
    datasets: List  # TODO - stricter
    offset: int
    count: int

class Version(BaseModel):
    type: Literal["dcat:Distribution"] = Field(alias="@type")
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
    type: List[str] = Field(alias="@type")
    title: str = Field(max_length=90)
    versions: List[Version]
    count: int
    offset: int

