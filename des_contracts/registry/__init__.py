"""Analyzer registry format.

Per rollout plan Wave 3.3 — a YAML manifest that any repo can contribute
to, listing analyzers with their eval metrics, fixture paths, status,
and maintainer. DES tutorials consume this to surface "ready analyzers"
as a sidebar.

The schema below IS the contract. Validation is done via
`validate_registry_entry()` — plain-dict-in, list-of-errors-out, no
framework dependency.

Example manifest:

    analyzers:
      yolo-vessel-hormuz:
        source: leo-constellation/edge-compute
        status: candidate
        eval_f1: 0.91
        eval_data: des_contracts_fixtures/hormuz_vessel_detections/
        maintainer: TobiasEdman
        precision_modes: [fp32, int8]
        supports_throttle: true
        version: 0.3.0

      sar-change-detector:
        source: leo-constellation/edge-compute
        status: candidate
        eval_f1: 0.87
        eval_data: des_contracts_fixtures/ukraine_sar_pairs/
        maintainer: TobiasEdman
"""
from __future__ import annotations

from typing import Any, Iterable

# Minimum fields every registry entry must provide.
REQUIRED_FIELDS = frozenset({
    "source",       # "<repo>/<subpath>" — where the implementation lives
    "status",       # one of AnalyzerStatus values
    "maintainer",   # GitHub handle or team name
    "version",      # analyzer semver
})

# Optional fields the registry understands and will surface.
KNOWN_FIELDS = REQUIRED_FIELDS | frozenset({
    "eval_f1",           # float, F1 on the fixture
    "eval_acc",          # float, accuracy
    "eval_miou",         # float, mean IoU for segmentation
    "eval_data",         # path (fixture / dataset) used for eval
    "precision_modes",   # list[str] subset of PrecisionMode values
    "supports_throttle", # bool — safe for resource-constrained deploy
    "notes",             # free-form markdown
})

VALID_STATUSES = frozenset({"candidate", "stable", "deprecated", "removed"})
VALID_PRECISIONS = frozenset({"fp32", "fp16", "bf16", "int8"})


def validate_registry_entry(name: str, entry: dict[str, Any]) -> list[str]:
    """Validate one registry entry. Returns list of human-readable errors.

    Empty list → entry is valid.

    Args:
        name: The analyzer's key in the manifest (e.g. "yolo-vessel-hormuz").
        entry: The dict of fields for this entry.
    """
    errors: list[str] = []

    # Required
    missing = REQUIRED_FIELDS - set(entry.keys())
    if missing:
        errors.append(f"{name}: missing required fields: {sorted(missing)}")

    # Status enum
    status = entry.get("status")
    if status is not None and status not in VALID_STATUSES:
        errors.append(
            f"{name}: status={status!r} not in {sorted(VALID_STATUSES)}"
        )

    # Precision-mode enum
    modes = entry.get("precision_modes")
    if modes is not None:
        if not isinstance(modes, list):
            errors.append(f"{name}: precision_modes must be a list")
        else:
            bad = [m for m in modes if m not in VALID_PRECISIONS]
            if bad:
                errors.append(
                    f"{name}: invalid precision_modes: {bad}; "
                    f"allowed: {sorted(VALID_PRECISIONS)}"
                )

    # Boolean
    if "supports_throttle" in entry and not isinstance(
        entry["supports_throttle"], bool
    ):
        errors.append(f"{name}: supports_throttle must be bool")

    # Metrics are floats in [0, 1]
    for metric in ("eval_f1", "eval_acc", "eval_miou"):
        if metric in entry:
            v = entry[metric]
            if not isinstance(v, (int, float)) or not (0.0 <= float(v) <= 1.0):
                errors.append(f"{name}: {metric}={v!r} must be float in [0, 1]")

    # Warn on unknown fields (non-fatal — just surfaces typos)
    unknown = set(entry.keys()) - KNOWN_FIELDS
    if unknown:
        errors.append(
            f"{name}: unknown fields (typo?): {sorted(unknown)}. "
            f"Known: {sorted(KNOWN_FIELDS)}"
        )

    return errors


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Validate a full registry manifest (top-level `analyzers:` dict).

    Returns a flat list of errors across all entries. Empty → valid.
    """
    errors: list[str] = []
    analyzers = manifest.get("analyzers")
    if not isinstance(analyzers, dict):
        return ["manifest: top-level 'analyzers:' must be a dict"]

    for name, entry in analyzers.items():
        if not isinstance(entry, dict):
            errors.append(f"{name}: entry must be a dict, got {type(entry).__name__}")
            continue
        errors.extend(validate_registry_entry(name, entry))

    return errors


def list_entries(manifest: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    """Yield (name, entry) pairs from a manifest. Skips non-dict entries silently."""
    for name, entry in manifest.get("analyzers", {}).items():
        if isinstance(entry, dict):
            yield name, entry


__all__ = [
    "REQUIRED_FIELDS",
    "KNOWN_FIELDS",
    "VALID_STATUSES",
    "VALID_PRECISIONS",
    "validate_registry_entry",
    "validate_manifest",
    "list_entries",
]
