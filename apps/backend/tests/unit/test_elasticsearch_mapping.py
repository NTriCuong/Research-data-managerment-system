import json
from pathlib import Path


MAPPING_PATH = (
    Path(__file__).resolve().parents[2]
    / "elasticsearch"
    / "rdms_research_objects_v1.json"
)


def load_mapping() -> dict:
    with MAPPING_PATH.open(encoding="utf-8") as mapping_file:
        return json.load(mapping_file)


def test_mapping_is_valid_strict_v1_definition():
    definition = load_mapping()

    assert definition["mappings"]["dynamic"] == "strict"
    assert definition["mappings"]["_meta"]["schema_version"] == 1
    assert definition["mappings"]["_meta"]["document_id"] == "research_id"


def test_vietnamese_analyzer_is_accent_insensitive():
    analysis = load_mapping()["settings"]["analysis"]
    analyzer = analysis["analyzer"]["rdms_vietnamese"]

    assert analyzer["tokenizer"] == "standard"
    assert analyzer["filter"] == ["lowercase", "rdms_ascii_folding"]
    assert analysis["filter"]["rdms_ascii_folding"]["type"] == "asciifolding"


def test_autocomplete_uses_ngrams_only_at_index_time():
    analyzers = load_mapping()["settings"]["analysis"]["analyzer"]

    assert "rdms_edge_ngram_2_20" in analyzers["rdms_autocomplete_index"]["filter"]
    assert "rdms_edge_ngram_2_20" not in analyzers["rdms_autocomplete_search"]["filter"]


def test_filter_fields_are_not_mapped_as_full_text():
    properties = load_mapping()["mappings"]["properties"]

    assert properties["research_id"]["type"] == "keyword"
    assert properties["access_level"]["type"] == "keyword"
    assert properties["year"]["type"] == "short"
    assert properties["is_current"]["type"] == "boolean"
    assert properties["department"]["properties"]["id"]["type"] == "keyword"
    assert properties["output_type"]["properties"]["id"]["type"] == "keyword"


def test_primary_search_fields_feed_combined_search_text():
    properties = load_mapping()["mappings"]["properties"]

    assert properties["title"]["copy_to"] == "search_text"
    assert properties["abstract"]["copy_to"] == "search_text"
    assert properties["description"]["copy_to"] == "search_text"
    assert properties["authors"]["properties"]["full_name"]["copy_to"] == "search_text"
    assert properties["keywords"]["properties"]["text"]["copy_to"] == "search_text"
    assert properties["domains"]["properties"]["name"]["copy_to"] == "search_text"
