import os
import pytest

from pydantic import ValidationError

from src.store.metadata.oxigraph.store import OxigraphMetadataStore
from src import schemas

# TODO - reimplenet as part of graph work

def test_oxigraph_get_publisher_returns_valid_structure():
     """
     Confirm that the OxigrapgMetadataStore.get_dataset()
     function returns a dataset that matches the dataset
     schema.
     """

     store = OxigraphMetadataStore()

     publisher = store.get_publisher("office-for-national-statistics")
     assert schemas.Publisher(**publisher).id == "https://staging.idpd.uk/publishers/office-for-national-statistics"


def test_oxigraph_get_publisher_returns_invalid_structure():
     """
     Confirm that the OxigrapgMetadataStore.get_dataset()
     function returns a dataset that matches the dataset
     schema.
     """

     store = OxigraphMetadataStore()

     publisher = store.get_publisher("office-for-national-statistics")

     # Sanity check that the schema validation is working as intended
     # i.e raises with wrong structure
     with pytest.raises(ValidationError):
        schemas.Publisher(**{"I": "break"})
