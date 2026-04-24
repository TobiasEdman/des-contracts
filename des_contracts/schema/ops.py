"""Numpy-based merge operations for the unified schema.

Kept in a submodule so `des_contracts.schema` stays numpy-free at import time.
Consumers that need the merge logic import this explicitly:

    from des_contracts.schema.ops import nmd19_to_unified, merge_all

Extracted verbatim from ImintEngine's imint/training/unified_schema.py at v5.
"""
from __future__ import annotations

try:
    import numpy as np
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "des_contracts.schema.ops requires numpy. Install it explicitly: "
        "`pip install numpy`. The base `des_contracts.schema` module does "
        "not require numpy — import the constants directly if you don't "
        "need the merge helpers."
    ) from e

from des_contracts.schema import (
    HARVEST_CLASS,
    NMD_TO_UNIFIED,
    NUM_UNIFIED_CLASSES,
    SJV_DEFAULT,
    SJV_TO_UNIFIED,
)

# Pre-built lookup array for NMD → Unified. 20 entries because raw NMD goes 0..19.
_NMD19_LUT = np.zeros(20, dtype=np.uint8)
for _src, _dst in NMD_TO_UNIFIED.items():
    _NMD19_LUT[_src] = _dst


def nmd19_to_unified(nmd_label: np.ndarray) -> np.ndarray:
    """Convert NMD raw 19-class labels to unified schema.

    Args:
        nmd_label: (H, W) uint8, NMD raw 19-class indices (0-19).

    Returns:
        (H, W) uint8, unified indices (0-22).
    """
    return _NMD19_LUT[np.clip(nmd_label, 0, 19)]


def merge_nmd_sjv(nmd_label: np.ndarray, sjv_codes: np.ndarray) -> np.ndarray:
    """Merge NMD 19-class labels with LPIS SJV grödkoder.

    SJV crop codes override NMD where parcels exist (sjv_codes > 0).

    Args:
        nmd_label: (H, W) uint8, NMD 19-class sequential indices (0-19).
        sjv_codes: (H, W) uint16, raw SJV grödkoder (0 = no parcel).

    Returns:
        (H, W) uint8, unified class indices (0-22).
    """
    unified = nmd19_to_unified(nmd_label)
    has_parcel = sjv_codes > 0
    if has_parcel.any():
        sjv_mapped = np.isin(sjv_codes, list(SJV_TO_UNIFIED.keys()))
        for sjv_code, unified_class in SJV_TO_UNIFIED.items():
            mask = sjv_codes == sjv_code
            if mask.any():
                unified[mask] = unified_class
        unified[has_parcel & ~sjv_mapped] = SJV_DEFAULT
    return unified


def merge_all(
    nmd_label: np.ndarray,
    lpis_mask: np.ndarray | None = None,
    harvest_mask: np.ndarray | None = None,
) -> np.ndarray:
    """Merge NMD 19-class + LPIS + SKS harvest into unified 23-class label.

    Semantic gating (raw NMD 19-class acts as gate for overlays):
      Forest (NMD 1–6)     + SKS clearcut → Hygge (22)
      Cropland (NMD 12–14) + LPIS parcel  → Crop class (9–21)
      Bebyggelse (9)                      → NMD wins, never overridden
      Vatten (10)                         → NMD wins, never overridden

    Priority: LPIS > SKS > NMD.

    Args:
        nmd_label: (H, W) uint8, NMD 19-class sequential indices (0-19).
        lpis_mask: (H, W) uint16, raw SJV grödkoder (0 = no parcel), or None.
        harvest_mask: (H, W) uint8, binary SKS harvest mask (0/1), or None.

    Returns:
        (H, W) uint8, unified class indices (0..22).
    """
    # Step 1: NMD baseline
    unified = nmd19_to_unified(nmd_label)
    nmd_base = unified.copy()

    # Step 2: LPIS crops — gate on raw NMD 19-class input.
    # NMD cropland (12) maps to background (0) in unified, so gating on
    # nmd_base would silently drop all LPIS parcels. Must use raw input.
    _NMD_AGRI_RAW = np.array([12, 13, 14], dtype=np.uint8)
    where_agri = np.isin(nmd_label, _NMD_AGRI_RAW)

    if lpis_mask is not None and where_agri.any():
        sjv_codes = np.asarray(lpis_mask, dtype=np.uint16)
        has_parcel = (sjv_codes > 0) & where_agri
        if has_parcel.any():
            sjv_mapped = np.isin(sjv_codes, list(SJV_TO_UNIFIED.keys()))
            for sjv_code, unified_class in SJV_TO_UNIFIED.items():
                mask = (sjv_codes == sjv_code) & where_agri
                if mask.any():
                    unified[mask] = unified_class
            unified[has_parcel & ~sjv_mapped] = SJV_DEFAULT

    # Step 3: SKS harvest — only where NMD says forest (unified 1–6)
    _NMD_FOREST = np.array([1, 2, 3, 4, 5, 6], dtype=np.uint8)
    where_forest = np.isin(nmd_base, _NMD_FOREST)

    if harvest_mask is not None and where_forest.any():
        unified[(harvest_mask > 0) & where_forest] = HARVEST_CLASS

    return unified


def get_class_weights(
    class_counts: dict[int, int],
    max_weight: float = 10.0,
) -> np.ndarray:
    """Compute inverse-frequency class weights, capped at max_weight.

    Args:
        class_counts: {class_idx: pixel_count}
        max_weight: Maximum weight (default 10×)

    Returns:
        (NUM_UNIFIED_CLASSES,) float32 weight array. Index 0 forced to 0.0.
    """
    total = sum(class_counts.values())
    weights = np.ones(NUM_UNIFIED_CLASSES, dtype=np.float32)
    for cls, count in class_counts.items():
        if 0 < cls < NUM_UNIFIED_CLASSES and count > 0:
            w = total / (NUM_UNIFIED_CLASSES * count)
            weights[cls] = min(w, max_weight)
    weights[0] = 0.0
    return weights


__all__ = [
    "nmd19_to_unified",
    "merge_nmd_sjv",
    "merge_all",
    "get_class_weights",
]
