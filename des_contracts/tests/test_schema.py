"""Contract tests for the 23-class unified schema.

These tests are the regression baseline for any future schema change.
If someone bumps SCHEMA_VERSION without updating the invariants here,
CI should catch it.
"""
from __future__ import annotations

import pytest

from des_contracts.schema import (
    HARVEST_CLASS,
    NMD_TO_UNIFIED,
    NUM_UNIFIED_CLASSES,
    SCHEMA_VERSION,
    SJV_DEFAULT,
    SJV_TO_UNIFIED,
    UNIFIED_CLASSES,
    UNIFIED_CLASS_NAMES,
    UNIFIED_COLORS,
    class_name,
)


def test_version_is_semver():
    parts = SCHEMA_VERSION.split(".")
    assert len(parts) == 3, f"SCHEMA_VERSION {SCHEMA_VERSION!r} must be MAJOR.MINOR.PATCH"
    for p in parts:
        assert p.isdigit(), f"non-numeric segment in SCHEMA_VERSION: {p!r}"


def test_class_count_is_23():
    assert NUM_UNIFIED_CLASSES == 23
    assert len(UNIFIED_CLASSES) == 23
    assert len(UNIFIED_CLASS_NAMES) == 23
    assert len(UNIFIED_COLORS) == 23


def test_class_ids_are_contiguous():
    assert set(UNIFIED_CLASSES.keys()) == set(range(NUM_UNIFIED_CLASSES))
    assert set(UNIFIED_COLORS.keys()) == set(range(NUM_UNIFIED_CLASSES))


def test_harvest_class_is_22():
    assert HARVEST_CLASS == 22
    assert UNIFIED_CLASSES[22] == "hygge"


def test_background_is_class_zero():
    assert UNIFIED_CLASSES[0] == "bakgrund"
    assert SJV_DEFAULT == 0


def test_forest_classes_1_through_6():
    """Forest + young-forest must occupy 1-6; merge_all's hygge overlay depends on this."""
    assert UNIFIED_CLASSES[1] == "tallskog"
    assert UNIFIED_CLASSES[2] == "granskog"
    assert UNIFIED_CLASSES[3] == "lövskog"
    assert UNIFIED_CLASSES[4] == "blandskog"
    assert UNIFIED_CLASSES[5] == "sumpskog"
    assert UNIFIED_CLASSES[6] == "tillfälligt ej skog"


def test_nmd_mapping_covers_full_range():
    # NMD-19 is keys 0..19 inclusive
    assert set(NMD_TO_UNIFIED.keys()) == set(range(20))


def test_nmd_cropland_maps_to_background():
    """NMD raw 12 = cropland must map to 0 — LPIS overlay is required for crop detail."""
    assert NMD_TO_UNIFIED[12] == 0


def test_nmd_forest_maps_to_forest():
    """NMD pine/spruce/deciduous/mixed → tallskog/granskog/lövskog/blandskog."""
    assert NMD_TO_UNIFIED[1] == 1
    assert NMD_TO_UNIFIED[2] == 2
    assert NMD_TO_UNIFIED[3] == 3
    assert NMD_TO_UNIFIED[4] == 4


def test_sjv_vete_codes():
    assert SJV_TO_UNIFIED[4] == 11   # höstvete
    assert SJV_TO_UNIFIED[5] == 11   # vårvete
    assert SJV_TO_UNIFIED[307] == 11 # speltvete


def test_sjv_majs_is_21():
    assert SJV_TO_UNIFIED[9] == 21


def test_sjv_potatis_codes():
    assert SJV_TO_UNIFIED[45] == 17  # matpotatis
    assert SJV_TO_UNIFIED[46] == 17  # stärkelsepotatis


def test_sjv_trada_maps_to_open_ground():
    """Träda (fallow, SJV 60) → öppen mark (8), not background."""
    assert SJV_TO_UNIFIED[60] == 8


def test_all_sjv_codes_map_to_valid_class():
    valid = set(range(NUM_UNIFIED_CLASSES))
    for sjv_code, unified_class in SJV_TO_UNIFIED.items():
        assert unified_class in valid, (
            f"SJV code {sjv_code} maps to invalid unified class {unified_class}"
        )


def test_class_name_helper():
    assert class_name(0) == "bakgrund"
    assert class_name(11) == "vete"
    assert class_name(22) == "hygge"
    with pytest.raises(KeyError):
        class_name(99)


def test_colors_are_rgb_tuples_in_0_255():
    for cls_id, rgb in UNIFIED_COLORS.items():
        assert isinstance(rgb, tuple), f"class {cls_id} color is {type(rgb).__name__}"
        assert len(rgb) == 3
        for channel in rgb:
            assert 0 <= channel <= 255, f"class {cls_id} has out-of-range channel {channel}"


def test_crop_classes_are_11_through_21():
    """Crops must occupy 11–21; harvest is 22; anything else breaks LPIS overlay gating."""
    for cls_id in range(11, 22):
        assert cls_id in UNIFIED_CLASSES
