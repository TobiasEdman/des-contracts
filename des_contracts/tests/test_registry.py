"""Tests for the analyzer registry validator."""
from des_contracts.registry import (
    validate_manifest,
    validate_registry_entry,
)


def _minimal_entry():
    return {
        "source": "leo-constellation/edge-compute",
        "status": "candidate",
        "maintainer": "TobiasEdman",
        "version": "0.3.0",
    }


def test_minimal_entry_validates():
    assert validate_registry_entry("test", _minimal_entry()) == []


def test_missing_required_field():
    entry = _minimal_entry()
    del entry["maintainer"]
    errs = validate_registry_entry("test", entry)
    assert any("maintainer" in e for e in errs)


def test_invalid_status():
    entry = _minimal_entry()
    entry["status"] = "unreleased"
    errs = validate_registry_entry("test", entry)
    assert any("unreleased" in e for e in errs)


def test_invalid_precision_mode():
    entry = _minimal_entry()
    entry["precision_modes"] = ["fp32", "fp4"]  # fp4 not allowed
    errs = validate_registry_entry("test", entry)
    assert any("fp4" in e for e in errs)


def test_precision_modes_must_be_list():
    entry = _minimal_entry()
    entry["precision_modes"] = "fp32"
    errs = validate_registry_entry("test", entry)
    assert any("must be a list" in e for e in errs)


def test_metric_out_of_range():
    entry = _minimal_entry()
    entry["eval_f1"] = 1.5
    errs = validate_registry_entry("test", entry)
    assert any("eval_f1" in e for e in errs)


def test_unknown_field_surfaced():
    entry = _minimal_entry()
    entry["precison_modes"] = ["fp32"]  # typo
    errs = validate_registry_entry("test", entry)
    assert any("precison_modes" in e for e in errs)


def test_manifest_happy_path():
    manifest = {
        "analyzers": {
            "yolo-vessel": {
                **_minimal_entry(),
                "eval_f1": 0.91,
                "supports_throttle": True,
                "precision_modes": ["fp32", "int8"],
            },
            "sar-change": _minimal_entry(),
        }
    }
    assert validate_manifest(manifest) == []


def test_manifest_top_level_shape():
    assert validate_manifest({}) == [
        "manifest: top-level 'analyzers:' must be a dict"
    ]
