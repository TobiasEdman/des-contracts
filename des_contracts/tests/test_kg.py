"""JSON Schema contract tests for KG exports."""
from __future__ import annotations

from des_contracts.kg import KG_CORE_SCHEMA, KG_VIEWS_SCHEMA, validate_against


def _minimal_kg_core():
    return {
        "schema_version": "1.0.0",
        "content_hash": "deadbeef",
        "_metadata": {"exported_at": "2026-04-24T12:00:00Z"},
        "domMeta": {},
        "domKeys": ["a"],
        "domainPos": {},
        "colors": {},
        "labels": {},
        "instColors": {"x": "#abc"},
        "nf": {},
        "merged": {"n": [], "e": []},
    }


def test_core_schema_has_id_and_type():
    assert KG_CORE_SCHEMA["$id"].endswith("kg_core.schema.json")
    assert KG_CORE_SCHEMA["type"] == "object"


def test_views_schema_has_id_and_type():
    assert KG_VIEWS_SCHEMA["$id"].endswith("kg_views.schema.json")
    assert KG_VIEWS_SCHEMA["type"] == "object"


def test_core_required_fields_present():
    required = set(KG_CORE_SCHEMA["required"])
    assert {"domMeta", "merged", "domKeys"} <= required


def test_views_required_fields_include_all_seven_views():
    required = set(KG_VIEWS_SCHEMA["required"])
    assert "themes" in required
    assert "v4n" in required
    assert "intlCoop" in required


def test_minimal_payload_validates():
    errs = validate_against(_minimal_kg_core(), KG_CORE_SCHEMA)
    assert errs == []


def test_missing_required_key_surfaced():
    payload = _minimal_kg_core()
    del payload["merged"]
    errs = validate_against(payload, KG_CORE_SCHEMA)
    assert any("merged" in e for e in errs)


def test_wrong_type_surfaced():
    payload = _minimal_kg_core()
    payload["domKeys"] = "not a list"
    errs = validate_against(payload, KG_CORE_SCHEMA)
    assert any("domKeys" in e for e in errs)


def test_nullable_metadata_allowed():
    payload = _minimal_kg_core()
    payload["content_hash"] = None
    payload["_metadata"] = None
    errs = validate_against(payload, KG_CORE_SCHEMA)
    assert errs == []
