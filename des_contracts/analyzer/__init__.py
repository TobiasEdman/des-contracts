"""Analyzer protocol and result types.

Per rollout plan Wave 3.3 + the leo+sdl report's "shared unlock" finding.

Every EO analyzer in the portfolio — whether it lives in ImintEngine
(production), leo-constellation/edge-compute (on-orbit), or
space-data-lab (notebook sandbox) — implements this Protocol so it can
graduate between repos without interface changes.

Design principles:
  - Zero runtime dependencies. This module is typing-only for consumers.
  - Protocol, not ABC — consumers don't have to subclass.
  - Results are plain dataclasses — JSON-serialisable, np.ndarray- and
    GeoTIFF-agnostic. Consumers carry heavy types in `data` field (dict)
    rather than the contract.
  - Throttle + precision-mode flags are optional — analyzers that don't
    care about on-orbit constraints just default them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, Protocol, runtime_checkable


class AnalyzerStatus(str, Enum):
    """Registry status of an analyzer."""

    CANDIDATE = "candidate"
    STABLE = "stable"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


PrecisionMode = Literal["fp32", "fp16", "bf16", "int8"]


@dataclass
class AnalyzerInput:
    """Input to an analyzer's run() call.

    Design note: we keep this deliberately minimal so every analyzer can
    accept it. Complex typed inputs (GeoTIFF paths, np.ndarray, PIL.Image,
    etc.) go in `data` as consumer-chosen keys. The contract is the field
    names here, not what's inside `data`.

    Attributes:
        aoi: Area of interest. Either a GeoJSON-geometry dict or a
            bbox tuple (min_lon, min_lat, max_lon, max_lat).
        temporal_range: ISO-8601 range string "YYYY-MM-DD/YYYY-MM-DD",
            or None for time-agnostic analyzers.
        data: Consumer-specific payload. Pass GeoTIFF paths, raster
            arrays, or whatever your analyzer expects.
        config: Configuration overrides from the caller, if any.
    """

    aoi: dict | tuple[float, float, float, float] | None = None
    temporal_range: str | None = None
    data: dict[str, Any] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyzerResult:
    """Result of an analyzer's run() call.

    Attributes:
        analyzer_name: The `name` of the analyzer that produced this.
        analyzer_version: The analyzer's version at run time.
        status: "success" | "failed" | "partial".
        data: Result payload (polygons, rasters, scores, etc.).
            Contents depend on the analyzer; not part of this contract.
        confidence: Overall confidence in [0.0, 1.0] if applicable.
        error: Error message if status != "success".
        metrics: Optional dict of eval metrics (f1, iou, latency_ms, etc.).
        metadata: Run metadata — timestamps, input hashes, model hash, etc.
    """

    analyzer_name: str
    analyzer_version: str
    status: Literal["success", "failed", "partial"] = "success"
    data: dict[str, Any] = field(default_factory=dict)
    confidence: float | None = None
    error: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Analyzer(Protocol):
    """Protocol every analyzer in the portfolio must satisfy.

    Usage:

        class MyYoloDetector:
            name = "yolo-vessel-hormuz"
            version = "0.3.0"
            supports_throttle = True
            precision_modes = ["fp32", "int8"]

            def configure(self, config: dict) -> None:
                self._threshold = config.get("confidence_threshold", 0.5)

            def run(self, input: AnalyzerInput) -> AnalyzerResult:
                ...

            def to_yaml_template(self) -> str:
                return "confidence_threshold: 0.5\\n..."

    Because this is a `runtime_checkable` Protocol, `isinstance(obj, Analyzer)`
    works without requiring explicit subclassing.
    """

    name: str
    version: str
    supports_throttle: bool
    precision_modes: list[PrecisionMode]

    def configure(self, config: dict[str, Any]) -> None:
        """Apply config. Called once before the first run()."""
        ...

    def run(self, input: AnalyzerInput) -> AnalyzerResult:
        """Execute the analysis. Must not mutate `input`."""
        ...

    def to_yaml_template(self) -> str:
        """Return a YAML skeleton of the analyzer's accepted config.

        The template should include every field `configure()` reads, with
        defaults filled in and a one-line comment per field. Used to
        generate `analyzer_config.yaml` scaffolds in consuming repos.
        """
        ...


__all__ = [
    "Analyzer",
    "AnalyzerInput",
    "AnalyzerResult",
    "AnalyzerStatus",
    "PrecisionMode",
]
