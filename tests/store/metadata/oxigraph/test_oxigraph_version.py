# import pytest

# from pydantic import ValidationError

# from store.metadata.oxigraph.store import OxigraphMetadataStore
# import schemas


# def test_oxigraph_get_version_returns_valid_structure():
#     """
#     Confirm that the OxigraphMetadataStore.get_version()
#     function returns a dictionary that matches the Version schema.
#     """
#     store = OxigraphMetadataStore()
#     version = store.get_version("cpih", "2022-01", "1")
#     version_schema = schemas.Version(**version)
#     assert (
#         version_schema.id
#         == "https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1"
#     )
#     assert "dcat:Distribution" in version_schema.type
#     assert "csvw:Table" in version_schema.type
#     assert len(version_schema.table_schema.columns) == 4


# def test_oxigraph_get_version_with_context_returns_valid_structure():
#     """
#     Confirm that the OxigraphMetadataStore.get_version()
#     function returns a dictionary that matches the VersionWithContext schema.
#     """
#     store = OxigraphMetadataStore()
#     version = store.get_version("cpih", "2022-01", "1")
#     version_schema = schemas.VersionWithContext(**version)
#     assert (
#         version_schema.id
#         == "https://staging.idpd.uk/datasets/cpih/editions/2022-01/versions/1"
#     )
#     assert "dcat:Distribution" in version_schema.type
#     assert "csvw:Table" in version_schema.type
#     assert len(version_schema.table_schema.columns) == 4
#     assert version_schema.context == "https://staging.idpd.uk/ns#"


# def test_version_schema_validation():
#     """Confirm that the schema validation is working as intended i.e raises ValidationError with wrong structure"""
#     with pytest.raises(ValidationError):
#         schemas.VersionWithContext(**{"I": "break"})
