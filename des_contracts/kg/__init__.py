"""JSON Schema for swedish-space-ecosystem KG exports.

Per rollout plan Wave 3.4 + the ecosystem-pair improvement report.

Previously the contract lived as Pydantic models in
swedish-space-ecosystem-v2/export/contract.py. Consumers outside that
repo (viz, des-agent, future SAC reports) had no way to validate
without importing the v2 source.

JSON Schema lets:
  - viz `2d.html` validate at fetch-time (`core.schema_version === "1.0.0"`)
  - des-agent verify payloads before ingestion
  - future tools generate types via json-schema-to-typescript / datamodel-codegen
  - CI in v2 diff this schema on each PR to detect unintended breaking changes

The Pydantic side of the contract (still in v2) is the generator; this
module is the downstream consumer-facing form.
"""
from __future__ import annotations

from typing import Any

# Shared metadata block used by both kg_core and kg_views (added Wave 1.6).
_METADATA_PROPERTIES: dict[str, Any] = {
    "schema_version": {
        "type": "string",
        "description": "KG contract version. Major bumps on breaking changes.",
    },
    "content_hash": {
        "type": ["string", "null"],
        "description": "SHA-256 of payload excluding schema_version/content_hash/_metadata.",
    },
    "_metadata": {
        "type": ["object", "null"],
        "description": "Freshness info populated by stamp_export().",
        "properties": {
            "exported_at": {"type": "string", "format": "date-time"},
            "neo4j_timestamp": {"type": ["string", "null"]},
            "record_counts": {"type": "object"},
        },
        "additionalProperties": True,
    },
}

KG_CORE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/TobiasEdman/des-contracts/kg_core.schema.json",
    "title": "kg_core.json",
    "description": (
        "Core data for the Swedish Space Ecosystem KG. Produced by "
        "swedish-space-ecosystem-v2 `make export`, consumed by "
        "swedish-space-ecosystem-viz and downstream tools."
    ),
    "type": "object",
    "required": [
        "domMeta",
        "domKeys",
        "domainPos",
        "colors",
        "labels",
        "instColors",
        "nf",
        "merged",
    ],
    "properties": {
        **_METADATA_PROPERTIES,
        "domMeta": {"type": "object"},
        "domKeys": {"type": "array", "items": {"type": "string"}},
        "domainPos": {"type": "object"},
        "colors": {"type": "object"},
        "labels": {"type": "object"},
        "instColors": {"type": "object", "additionalProperties": {"type": "string"}},
        "nf": {"type": "object"},
        "merged": {
            "type": "object",
            "required": ["n", "e"],
            "properties": {
                "n": {
                    "type": "array",
                    "description": "Nodes. Each must include id, and typically domain + type.",
                },
                "e": {
                    "type": "array",
                    "description": "Edges. Each has s (source id), t (target id), tp (type), w (weight).",
                    "items": {
                        "type": "object",
                        "required": ["s", "t", "tp", "w"],
                        "properties": {
                            "s": {"type": "string"},
                            "t": {"type": "string"},
                            "tp": {"type": "string"},
                            "w": {"type": "number"},
                            "sl": {"type": ["string", "null"]},
                            "tl": {"type": ["string", "null"]},
                        },
                    },
                },
            },
        },
    },
    "additionalProperties": True,
}


KG_VIEWS_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://github.com/TobiasEdman/des-contracts/kg_views.schema.json",
    "title": "kg_views.json",
    "description": (
        "Per-view data structures for the Swedish Space Ecosystem KG. "
        "Seven views: Themes, Institutions, Researchers, System, Industry, "
        "Intl Cooperation, plus a collaboration (V4) network. "
        "Produced by swedish-space-ecosystem-v2, consumed by -viz."
    ),
    "type": "object",
    "required": [
        "themes",
        "themeLinks",
        "sweInst",
        "intlInst",
        "sweLinks",
        "intlLinks",
        "resNodes",
        "resLinks",
        "sysSwInst",
        "sysIntlInst",
        "sysRes",
        "sysIntlRes",
        "sysAffLinks",
        "sysIntlAffLinks",
        "sysCrossLinks",
        "sysResIntlLinks",
        "sysSwLinks",
        "sysIntlLinks",
        "v4n",
        "v4e",
        "intlCoop",
    ],
    "properties": {
        **_METADATA_PROPERTIES,
        # V1 Themes
        "themes": {"type": "array"},
        "themeLinks": {"type": "array"},
        # V2 Institutions
        "sweInst": {"type": "object"},
        "intlInst": {"type": "object"},
        "sweLinks": {"type": "array"},
        "intlLinks": {"type": "array"},
        # V3 Researchers
        "resNodes": {"type": "array"},
        "resLinks": {"type": "array"},
        # V4 System network
        "sysSwInst": {"type": "array"},
        "sysIntlInst": {"type": "array"},
        "sysRes": {"type": "array"},
        "sysIntlRes": {"type": "array"},
        "sysAffLinks": {"type": "array"},
        "sysIntlAffLinks": {"type": "array"},
        "sysCrossLinks": {"type": "array"},
        "sysResIntlLinks": {"type": "array"},
        "sysSwLinks": {"type": "array"},
        "sysIntlLinks": {"type": "array"},
        # V5 Industry
        "v4n": {"type": "array"},
        "v4e": {"type": "array"},
        # V7 International cooperation
        "intlCoop": {"type": "object"},
    },
    "additionalProperties": True,
}


def validate_against(
    payload: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    """Lightweight stdlib validator. Returns list of errors; empty = valid.

    Checks top-level required keys + top-level type of each key. Does NOT
    recurse — if you want full JSON Schema validation, install `jsonschema`
    and use `jsonschema.validate(payload, schema)`. The goal of this
    helper is fast smoke-check without adding a dep.
    """
    errors: list[str] = []

    required = schema.get("required", [])
    missing = [k for k in required if k not in payload]
    if missing:
        errors.append(f"missing required keys: {missing}")

    props = schema.get("properties", {})
    for key, spec in props.items():
        if key not in payload:
            continue
        expected = spec.get("type")
        if expected is None:
            continue
        got = payload[key]
        if isinstance(expected, list):
            allowed_types = expected
        else:
            allowed_types = [expected]
        type_ok = False
        for t in allowed_types:
            if t == "object" and isinstance(got, dict):
                type_ok = True
            elif t == "array" and isinstance(got, list):
                type_ok = True
            elif t == "string" and isinstance(got, str):
                type_ok = True
            elif t == "number" and isinstance(got, (int, float)) and not isinstance(got, bool):
                type_ok = True
            elif t == "integer" and isinstance(got, int) and not isinstance(got, bool):
                type_ok = True
            elif t == "boolean" and isinstance(got, bool):
                type_ok = True
            elif t == "null" and got is None:
                type_ok = True
        if not type_ok:
            errors.append(
                f"{key!r}: expected {expected}, got {type(got).__name__}"
            )

    return errors


__all__ = [
    "KG_CORE_SCHEMA",
    "KG_VIEWS_SCHEMA",
    "validate_against",
]
