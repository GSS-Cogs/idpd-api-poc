# import os
# import pytest

# from pydantic import ValidationError

# from src.store.metadata.oxigraph.store import OxigraphMetadataStore
# from src import schemas


# def test_oxigraph_get_publisher_returns_valid_structure():
#     """
#     Confirm that the OxigraphMetadataStore.get_publisher()
#     function returns a dictionary that matches the Publisher
#     schema.
#     """

#     store = OxigraphMetadataStore()
#     publisher = store.get_publisher("office-for-national-statistics")
#     publisher_schema = schemas.Publisher(**publisher)
#     assert (
#         publisher_schema.id
#         == "https://staging.idpd.uk/publishers/office-for-national-statistics"
#     )
#     assert publisher_schema.type == "dcat:publisher"


# def test_oxigraph_get_publisher_with_context_returns_valid_structure():
#     """
#     Confirm that the OxigraphMetadataStore.get_publisher()
#     function returns a dictionary that matches the PublisherWithContext schema.
#     """

#     store = OxigraphMetadataStore()
#     publisher = store.get_publisher("office-for-national-statistics")
#     publisher_schema = schemas.PublisherWithContext(**publisher)
#     assert (
#         publisher_schema.id
#         == "https://staging.idpd.uk/publishers/office-for-national-statistics"
#     )
#     assert publisher_schema.type == "dcat:publisher"
#     assert publisher_schema.context == "https://staging.idpd.uk/ns#"


# def test_oxigraph_get_publisher_returns_invalid_structure():
#     """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
#     with pytest.raises(ValidationError):
#         schemas.Publisher(**{"I": "break"})


# def test_oxigraph_get_publisher_with_context_returns_invalid_structure():
#     """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
#     with pytest.raises(ValidationError):
#         schemas.PublisherWithContext(**{"I": "break"})
