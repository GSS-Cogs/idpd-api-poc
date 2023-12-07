"""
This module defines the pydantic models for the API. The schemas are used to
validate the structure of the data returned by the API.
"""

from ast import alias
from enum import Enum
from typing import List, Literal, Optional, Union
from typing_extensions import Annotated

from pydantic import BaseModel, Field, AwareDatetime
from pydantic.functional_validators import AfterValidator

from src.validation import validate_time

time_value = Annotated[str, AfterValidator(validate_time)]

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
    threeTimesAMonth = "three_times_a_month"
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
    start: str = time_value
    end: str = time_value


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


class SummarisedVersion(BaseModel):
    """
    A short form schema for Version as presented
    at the /editions level
    """

    id: str = Field(alias="@id")
    issued: str = AwareDatetime
    modified: str = AwareDatetime


class Edition(BaseModel):
    id: str = Field(alias="@id")
    type: Literal["dcat:Dataset"] = Field(alias="@type")
    in_series: str
    identifier: str
    title: str = Field(max_length=90)
    summary: str = Field(max_length=500)
    description: str = Field(max_length=500)
    publisher: str
    creator: str
    contact_point: ContactPoint
    topics: Union[str, List[str]]
    frequency: Frequency
    keywords: list[str]
    licence: str
    issued: str = AwareDatetime
    modified: str = AwareDatetime
    spatial_resolution: list[str]
    spatial_coverage: str = Field(pattern=r"^[EJKLMNSW]{1}\d{8}$")
    temporal_resolution: list[str]
    temporal_coverage: PeriodOfTime
    next_release: str = AwareDatetime
    versions_url: str
    versions: List[SummarisedVersion]
    table_schema: TableSchema


class EditionWithContext(Edition):
    context: str = Field(alias="@context")


class SummarisedEdition(BaseModel):
    """
    A short form schema for Edition as presented
    at the /datasets level
    """

    id: str = Field(alias="@id")
    issued: str = AwareDatetime
    modified: str = AwareDatetime


class Editions(BaseModel):
    context: str = Field(alias="@context")
    id: str = Field(alias="@id")
    type: Literal["hydra:Collection"] = Field(alias="@type")
    title: str = Field(max_length=90)
    editions: List[Edition]


# If we wanted to provide the ability to attach arbitrary RDF we might want to
# look at https://github.com/pydantic/pydantic/discussions/5853
class Dataset(BaseModel):
    id: str = Field(alias="@id")
    type: Literal["dcat:DatasetSeries"] = Field(alias="@type")
    identifier: str
    title: str = Field(max_length=90)
    summary: str = Field(max_length=500)
    description: str = Field(max_length=500)
    issued: str = AwareDatetime
    modified: str = AwareDatetime
    next_release: str = AwareDatetime
    publisher: str
    creator: str
    contact_point: ContactPoint
    topics: Union[str, List[str]]
    frequency: Frequency
    keywords: list[str]
    licence: str
    spatial_resolution: Union[str, list[str]]
    spatial_coverage: str = Field(pattern=r"^[EJKLMNSW]{1}\d{8}$")
    temporal_resolution: Union[str, list[str]]
    temporal_coverage: PeriodOfTime
    editions: List[SummarisedEdition]
    editions_url: str


class DatasetWithContext(Dataset):
    context: str = Field(alias="@context")


class Datasets(BaseModel):
    context: str = Field(alias="@context")
    id: str = Field(alias="@id")
    type: List[str] = Field(alias="@type")
    datasets: List[Dataset]
    offset: int
    count: int


class Version(BaseModel):
    type: List[str] = Field(alias="@type")
    id: str = Field(alias="@id")
    identifier: str
    issued: str = AwareDatetime
    title: str = Field(max_length=90)
    summary: str = Field(max_length=500)
    description: str = Field(max_length=500)
    download_url: str
    media_type: str
    table_schema: TableSchema


class VersionWithContext(Version):
    context: str = Field(alias="@context")


class Versions(BaseModel):
    context: str = Field(alias="@context")
    id: str = Field(alias="@id")
    type: Literal["hydra:Collection"] = Field(alias="@type")
    title: str = Field(max_length=90)
    versions: List[Version]
    count: int
    offset: int


class Publisher(BaseModel):
    id: str = Field(alias="@id")
    type: Literal["dcat:publisher"] = Field(alias="@type")
    title: str = Field(max_length=90)
    description: str
    landing_page: str


class PublisherWithContext(Publisher):
    context: str = Field(alias="@context")


class Publishers(BaseModel):
    context: Optional[str] = Field(alias="@context")
    id: str = Field(alias="@id")
    type: Literal["hydra:Collection"] = Field(alias="@type")
    publishers: List[Publisher]
    count: int
    offset: int


class Topic(BaseModel):
    id: str = Field(alias="@id")
    type: Literal["dcat:theme"] = Field(alias="@type")
    identifier: str
    title: str = Field(max_length=90)
    description: str = Field(max_length=500)
    sub_topics: Union[List[str], None] = Field(default_factory=list)
    parent_topics: Union[List[str], None] = Field(default_factory=list)


class TopicWithContext(Topic):
    context: str = Field(alias="@context")


class Topics(BaseModel):
    context: str = Field(alias="@context")
    id: str = Field(alias="@id")
    type: Literal["hydra:Collection"] = Field(alias="@type")
    topics: List[Topic]
    count: int
    offset: int
