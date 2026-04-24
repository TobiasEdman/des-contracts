"""Unified 23-class LULC schema — NMD + LPIS + SKS.

Extracted from ImintEngine v5 (commit `fc72078`) to des-contracts v0.1.0
per rollout plan Wave 3.2. The numpy-based merge_all()/nmd19_to_unified()
helpers live in `des_contracts.schema.ops` as an optional module so this
package's core imports stay numpy-free.

The schema IS the contract. Every consumer of this module is committing
to:
  - the 23-class enumeration (0..22)
  - the Swedish class names (do not translate — they carry domain meaning)
  - the SJV-code → class mapping (LPIS grödkoder 2018–2026)
  - the NMD-19 → class mapping (no raw cropland — requires LPIS)
  - the RGB color palette (for dashboards; consumer-visible brand)

Breaking any of these requires a MAJOR version bump of des-contracts.
"""
from __future__ import annotations

# Schema version. Bump on ANY breaking change:
#   - add/remove/rename a class
#   - change a class's NMD or SJV mapping
#   - change the num_classes total
#
# Patch-bump for documentation or color-palette cosmetic tweaks only.
SCHEMA_VERSION = "5.0.0"

NUM_UNIFIED_CLASSES = 23

UNIFIED_CLASSES: dict[int, str] = {
    0: "bakgrund",              # ignore_index
    # NMD-derived (1-10)
    1: "tallskog",              # NMD: forest_pine
    2: "granskog",              # NMD: forest_spruce
    3: "lövskog",               # NMD: forest_deciduous
    4: "blandskog",             # NMD: forest_mixed
    5: "sumpskog",              # NMD: forest_wetland (all subtypes)
    6: "tillfälligt ej skog",   # NMD raw 5: clearcut regrowth / young forest
    7: "våtmark",               # NMD: open_wetland
    8: "öppen mark",            # NMD: open_land
    9: "bebyggelse",            # NMD: developed
    10: "vatten",               # NMD: water
    # LPIS crop detail (11-21) — replaces NMD cropland
    11: "vete",                 # SJV 4, 5, 29, 307
    12: "korn",                 # SJV 1, 2, 12, 13, 315
    13: "havre",                # SJV 3, 10, 15
    14: "oljeväxter",           # SJV 20-28, 38, 40-42, 85-88
    15: "slåttervall",          # SJV 49, 50, 57-59, 62, 63, 302, 16, 80, 81
    16: "bete",                 # SJV 52-56, 61, 89, 90, 95
    17: "potatis",              # SJV 45, 46, 70-72, 311
    18: "sockerbetor",          # SJV 47, 48
    19: "trindsäd",             # SJV 30-37, 39, 43
    20: "råg",                  # SJV 7, 8, 11, 14, 29, 317
    21: "majs",                 # SJV 9 — C4, spectrally distinct
    # SKS harvest (22)
    22: "hygge",                # SKS utförda avverkningar
}

UNIFIED_CLASS_NAMES: list[str] = [UNIFIED_CLASSES[i] for i in range(NUM_UNIFIED_CLASSES)]

# Color palette (RGB tuples, 0-255 per channel)
# Index-aligned with UNIFIED_CLASS_NAMES.
UNIFIED_COLORS: dict[int, tuple[int, int, int]] = {
    0: (0, 0, 0),
    1: (0, 100, 0),
    2: (34, 139, 34),
    3: (50, 205, 50),
    4: (60, 179, 113),
    5: (46, 79, 46),
    6: (160, 200, 120),
    7: (139, 90, 43),
    8: (210, 180, 140),
    9: (255, 0, 0),
    10: (0, 0, 255),
    11: (230, 180, 34),
    12: (212, 130, 23),
    13: (255, 255, 100),
    14: (45, 180, 90),
    15: (100, 200, 100),
    16: (80, 160, 60),
    17: (180, 80, 40),
    18: (200, 100, 200),
    19: (140, 180, 50),
    20: (190, 150, 80),
    21: (220, 200, 0),
    22: (0, 206, 209),
}

UNIFIED_COLOR_LIST: list[tuple[int, int, int]] = [
    UNIFIED_COLORS[i] for i in range(NUM_UNIFIED_CLASSES)
]


# ── NMD raw 19-class → Unified mapping ────────────────────────────────────────
# NMD raw 19-class (from ImintEngine class_schema.nmd_raster_to_lulc):
#   0=bg, 1=pine, 2=spruce, 3=deciduous, 4=mixed, 5=temp_non_forest,
#   6-10=wetland_forest variants, 11=open_wetland, 12=cropland,
#   13-14=open_land, 15-17=developed, 18-19=water
#
# Stored as plain dict for numpy-free import. Consumers that want an
# np.ndarray lookup table can build one from this dict or import from
# des_contracts.schema.ops.
NMD_TO_UNIFIED: dict[int, int] = {
    0: 0,     # background
    1: 1,     # forest_pine → tallskog
    2: 2,     # forest_spruce → granskog
    3: 3,     # forest_deciduous → lövskog
    4: 4,     # forest_mixed → blandskog
    5: 6,     # forest_temp_non_forest → tillfälligt ej skog
    6: 5,     # forest_wetland_pine → sumpskog
    7: 5,     # forest_wetland_spruce → sumpskog
    8: 5,     # forest_wetland_deciduous → sumpskog
    9: 5,     # forest_wetland_mixed → sumpskog
    10: 5,    # forest_wetland_temp → sumpskog
    11: 7,    # open_wetland → våtmark
    12: 0,    # cropland → background (unknown without LPIS parcel)
    13: 8,    # open_land_bare → öppen mark
    14: 8,    # open_land_vegetated → öppen mark
    15: 9,    # developed_buildings → bebyggelse
    16: 9,    # developed_infrastructure → bebyggelse
    17: 9,    # developed_roads → bebyggelse
    18: 10,   # water_lakes → vatten
    19: 10,   # water_sea → vatten
}

# ── SJV grödkod → Unified class mapping ──────────────────────────────────────
# Direct mapping from SJV crop codes (grdkod_mar) to unified class.
# Codes are consistent across years 2018–2026. New codes were added
# from 2022 onward but existing ones did not change semantically.
# Source: Jordbruksverket grödkodslista 2026 + areal-verifiering mot LPIS.
SJV_TO_UNIFIED: dict[int, int] = {
    # Vete (11)
    4: 11, 5: 11, 307: 11, 316: 11,
    # Korn (12)
    1: 12, 2: 12, 12: 12, 13: 12, 315: 12,
    # Havre (13)
    3: 13, 10: 13, 15: 13,
    # Oljeväxter (14)
    20: 14, 21: 14, 22: 14, 23: 14, 24: 14,
    25: 14, 26: 14, 27: 14, 28: 14,
    38: 14, 40: 14, 41: 14, 42: 14,
    85: 14, 86: 14, 87: 14, 88: 14,
    # Slåttervall (15) incl. grönfoder
    49: 15, 50: 15, 57: 15, 58: 15, 59: 15,
    62: 15, 63: 15, 302: 15, 308: 15,
    6: 15, 301: 15, 300: 15,
    16: 15, 67: 15, 68: 15, 80: 15, 81: 15,
    # Bete (16)
    52: 16, 53: 16, 54: 16, 55: 16, 56: 16,
    61: 16, 89: 16, 90: 16, 95: 16,
    # Potatis (17)
    45: 17, 46: 17, 311: 17,
    70: 17, 71: 17, 72: 17,
    # Sockerbetor (18)
    47: 18, 48: 18,
    # Trindsäd (19)
    30: 19, 31: 19, 32: 19, 33: 19, 34: 19,
    35: 19, 36: 19, 37: 19, 39: 19, 43: 19,
    # Råg (20)
    7: 20, 8: 20, 29: 20, 317: 20,
    11: 20, 14: 20,
    # Majs (21) — C4 photosynthesis
    9: 21,
    # Träda/fallow → öppen mark (8) — bare or sparse vegetation
    60: 8,
    # Unmapped codes (skyddszon 66/77, grönsaksodling 74, kryddväxter 79) fall
    # through to SJV_DEFAULT=0 (background). Intentional — sub-pixel geometry
    # or insufficient spectral contrast for reliable training.
}

# Default for unmapped SJV codes — background so unknown cropland does not
# contaminate training with spectrally heterogeneous noise.
SJV_DEFAULT: int = 0

# Harvest class index (SKS utförda avverkningar)
HARVEST_CLASS: int = 22


def class_name(cls_id: int) -> str:
    """Return the Swedish class name for a unified class id.

    Raises:
        KeyError if cls_id is not in 0..22.
    """
    return UNIFIED_CLASSES[cls_id]


__all__ = [
    "SCHEMA_VERSION",
    "NUM_UNIFIED_CLASSES",
    "UNIFIED_CLASSES",
    "UNIFIED_CLASS_NAMES",
    "UNIFIED_COLORS",
    "UNIFIED_COLOR_LIST",
    "NMD_TO_UNIFIED",
    "SJV_TO_UNIFIED",
    "SJV_DEFAULT",
    "HARVEST_CLASS",
    "class_name",
]
