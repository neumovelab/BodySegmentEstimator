"""
api_to_poser_bridge.py
======================
Converts SubjectMeasures JSON output → Dict[str, SegmentSpec]
ready to drop into poser_render.py instead of build_segment_specs().

Usage
-----
    from api_to_poser_bridge import build_specs_from_api
    from poser_render import render  # or however you call the renderer

    import json
    with open("sample_segment_model.json") as f:
        api_dict = json.load(f)

    specs = build_specs_from_api(api_dict)
    # pass specs to your renderer exactly where build_segment_specs() was used

Units
-----
- API JSON lengths / circumferences / breadths are in **cm** → converted to m here
- SegmentSpec lengths and radii are in **meters**
- If a circumference key is missing the code falls back to the healthy baseline radius
"""

import math
import copy
import numpy as np
from dataclasses import dataclass
from typing import Dict, Literal, Optional, Tuple


# ---------------------------------------------------------------------------
# SegmentSpec (copy from poser_render.py so this file is self-contained)
# ---------------------------------------------------------------------------
@dataclass
class SegmentSpec:
    name: str
    shape: Literal["frustum", "cone", "ellipsoid"]
    length: float
    res: int
    color: np.ndarray
    r_bottom: Optional[Tuple[float, float]] = None
    r_top:    Optional[Tuple[float, float]] = None
    off_top:  Optional[Tuple[float, float]] = None
    r:        Optional[Tuple[float, float]] = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
CM = 1 / 100          # cm → m conversion factor
RES = 100             # mesh resolution (matches poser baseline)


def _circ_to_r(circumference_cm: float) -> float:
    """Circular approximation: radius from circumference (cm) → meters."""
    return (circumference_cm * CM) / (2 * math.pi)


def _ellipse_from_breadth_depth(breadth_cm: float, depth_cm: float) -> Tuple[float, float]:
    """Half-breadth, half-depth → (rx, rz) in meters (elliptical cross-section)."""
    return (breadth_cm * CM / 2, depth_cm * CM / 2)


def _scaled_baseline_from_circ(circumference_cm: float, baseline_pair: Tuple[float, float]) -> Tuple[float, float]:
    """
    Scale baseline ellipse by equivalent circular radius from circumference.
    This preserves the baseline anisotropy (helps avoid cylinder-like feet/thighs).
    """
    r_eq = _circ_to_r(circumference_cm)
    base_eq = math.sqrt(max(1e-9, baseline_pair[0] * baseline_pair[1]))
    s = r_eq / base_eq
    return (baseline_pair[0] * s, baseline_pair[1] * s)


def _swap_xz(pair: Tuple[float, float]) -> Tuple[float, float]:
    """Swap mesh X/Z radii to rotate cross-section orientation by 90 deg."""
    return (pair[1], pair[0])


def _color(r, g, b) -> np.ndarray:
    return np.array([r, g, b], dtype=float) / 255.0


def _get(d: dict, *keys, default=None):
    """Safe nested dict get."""
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


# ---------------------------------------------------------------------------
# Baseline colors (from poser_render.py)
# ---------------------------------------------------------------------------
FEMALE_COLORS = {
    "foot":         _color(241, 184, 197),
    "shank":        _color(236, 170, 188),
    "thigh":        _color(231, 156, 179),
    "thigh2":       _color(233, 162, 183),
    "lower_torso":  _color(226, 142, 169),
    "lower_torso2": _color(229, 149, 173),
    "middle_torso": _color(222, 132, 162),
    "upper_torso":  _color(216, 121, 154),
    "upper_torso2": _color(219, 126, 158),
    "upper_arm":    _color(228, 146, 173),
    "lower_arm":    _color(233, 162, 183),
    "hand":         _color(241, 184, 197),
    "head":         _color(210, 110, 145),
}

MALE_COLORS = {
    "foot":         _color(188, 214, 240),
    "shank":        _color(170, 202, 232),
    "thigh":        _color(152, 190, 224),
    "thigh2":       _color(160, 196, 228),
    "lower_torso":  _color(138, 178, 214),
    "lower_torso2": _color(145, 184, 218),
    "middle_torso": _color(126, 168, 206),
    "upper_torso":  _color(114, 157, 196),
    "upper_torso2": _color(120, 162, 201),
    "upper_arm":    _color(136, 176, 212),
    "lower_arm":    _color(160, 196, 228),
    "hand":         _color(188, 214, 240),
    "head":         _color(104, 145, 186),
}


# ---------------------------------------------------------------------------
# Healthy baseline radii (meters) — fallback when API key is missing
# ---------------------------------------------------------------------------
BASELINE = {
    # foot
    "r_bottom_foot": (0.02,  0.045),
    "r_top_foot":    (0.01,  0.04),
    # shank / thigh knee
    "r_top_shank":   (0.06,  0.05),
    "r_top_thigh":   (0.09,  0.0925),
    # torso
    "r_bottom_lower": (0.14, 0.18),
    "r_top_lower":    (0.13, 0.17),
    "r_top_mid":      (0.13, 0.19),
    "r_top_upper":    (0.12, 0.22),
    "r_top_upper2":   (0.05, 0.08),
    # arm
    "r_shoulder":     (0.04, 0.04),
    "r_elbow":        (0.03, 0.03),
    "r_wrist":        (0.02, 0.02),
    # head
    "r_head":         (0.09, 0.10),
    "r_hand":         (0.035, 0.035),
    # baseline lengths (m)
    "L_foot":        0.21,
    "L_shank":       0.45,
    "L_thigh":       0.45,
    "L_thigh2":      0.12,
    "L_lower_torso": 0.18,
    "L_lower_torso2":0.12,
    "L_middle_torso":0.25,
    "L_upper_torso": 0.18,
    "L_upper_torso2":0.12,
    "L_upper_arm":   0.30,
    "L_lower_arm":   0.28,
    "L_hand":        0.08,
    "L_head":        0.25,
}

# Torso split fractions (must sum to 1.0 per logical segment)
# LowerTorso → lower_torso2 (cone cap) + lower_torso (main frustum)
LOWER_TORSO_CAP_FRAC  = 0.40   # lower_torso2 cone
LOWER_TORSO_MAIN_FRAC = 0.60   # lower_torso frustum

# Thigh → r_thigh (main frustum) + r_thigh2 (cone cap at hip)
THIGH_MAIN_FRAC = 0.79
THIGH_CAP_FRAC  = 0.21


# Foot mesh height tuning (meters) when using circumference-derived radii.
FOOT_HEIGHT_MIN_M = 0.075
FOOT_HEIGHT_MAX_M = 0.18
FOOT_HEEL_OFFSET_MAX_M = 0.035
# Extra global scaling so overall subject size (via Foot.length) also affects
# foot cross-section thickness, not only ball/ankle circumferences.
FOOT_RADIUS_SCALE_FROM_LENGTH_MIN = 0.90
FOOT_RADIUS_SCALE_FROM_LENGTH_MAX = 1.35


# ---------------------------------------------------------------------------
# Core bridge
# ---------------------------------------------------------------------------
def build_specs_from_api(api: dict, sex: Optional[str] = None) -> Dict[str, SegmentSpec]:
    """
    Parameters
    ----------
    api : dict
        The dict loaded from SubjectMeasures JSON output
        (top-level keys: "segments", "all_measures").

    Returns
    -------
    Dict[str, SegmentSpec]  — 20 entries, same keys as SEGMENT_NAMES in poser_render.py
    """
    segs   = api.get("segments", {})
    circs  = api.get("all_measures", {}).get("circumferences", {})
    add    = api.get("all_measures", {}).get("additional", {})
    palette = MALE_COLORS if (sex or "").lower() == "male" else FEMALE_COLORS

    # ── Helper: pull segment length (cm → m), fall back to baseline
    def seg_len(api_key: str, baseline_key: str) -> float:
        v = _get(segs, api_key, "length")
        return v * CM if v is not None else BASELINE[baseline_key]

    # ── Helper: elliptical radius pair from circumference (baseline-shape scaled) or breadth/depth
    def r_from_circ(circ_key: str, baseline_key: str) -> Tuple[float, float]:
        v = circs.get(circ_key)
        if v is not None:
            return _scaled_baseline_from_circ(v, BASELINE[baseline_key])
        return BASELINE[baseline_key]

    def r_from_bd(b_key: str, d_key: str, baseline_key: str) -> Tuple[float, float]:
        b = add.get(b_key)
        d = add.get(d_key)
        if b and d:
            return _ellipse_from_breadth_depth(b, d)
        return BASELINE[baseline_key]

    # ------------------------------------------------------------------
    # Extract subject-specific radii
    # ------------------------------------------------------------------

    # Foot
    r_bot_foot = r_from_circ("balloffoot", "r_bottom_foot")
    r_top_foot = r_from_circ("ankle",      "r_top_foot")
    foot_len_api_m = seg_len("Foot", "L_foot")
    foot_radius_len_scale = foot_len_api_m / BASELINE["L_foot"]
    foot_radius_len_scale = max(
        FOOT_RADIUS_SCALE_FROM_LENGTH_MIN,
        min(FOOT_RADIUS_SCALE_FROM_LENGTH_MAX, foot_radius_len_scale),
    )
    r_bot_foot = (r_bot_foot[0] * foot_radius_len_scale, r_bot_foot[1] * foot_radius_len_scale)
    r_top_foot = (r_top_foot[0] * foot_radius_len_scale, r_top_foot[1] * foot_radius_len_scale)

    # Shank / knee
    r_top_shank = r_from_circ("calf",  "r_top_shank")
    r_bot_shank = r_top_foot           # shank bottom = foot top (ankle)

    # Thigh / knee
    r_top_thigh  = r_from_circ("thigh",      "r_top_thigh")
    r_bot_thigh  = r_from_circ("lowerthigh", "r_top_shank")   # just above knee

    # Rotate lower-limb mesh orientation (without changing cameras): swap X/Z
    # cross-section axes so front/side view leg appearance is exchanged.
    r_bot_foot = _swap_xz(r_bot_foot)
    r_top_foot = _swap_xz(r_top_foot)
    r_top_shank = _swap_xz(r_top_shank)
    r_bot_shank = _swap_xz(r_bot_shank)
    r_top_thigh = _swap_xz(r_top_thigh)
    r_bot_thigh = _swap_xz(r_bot_thigh)

    # Foot segment "length" in poser acts like vertical thickness in this pose setup.
    # Prefer API Foot.length so rendered feet track measured subject scale.
    # Keep a modest floor/ceiling to avoid extreme artifacts from outlier inputs.
    foot_height_est = foot_len_api_m

    # Torso — use breadth/depth where available, else circumference
    r_bot_lower  = r_from_bd("hipbreadth",   "buttockdepth",  "r_bottom_lower")
    r_top_lower  = r_from_bd("waistbreadth", "waistdepth",    "r_top_lower")
    r_top_mid    = r_from_bd("chestbreadth", "chestdepth",    "r_top_mid")
    r_top_upper  = r_from_bd("biacromialbreadth", "chestdepth", "r_top_upper")

    # Shoulder/neck transition for upper torso top
    r_top_upper2 = r_from_circ("neckbase", "r_top_upper2")

    # Arm
    r_shoulder = r_from_circ("biceps", "r_shoulder")
    r_elbow    = r_from_circ("forearm",  "r_elbow")
    r_wrist    = r_from_circ("wrist",    "r_wrist")

    # Hand
    r_hand  = r_from_circ("hand", "r_hand")

    # Head
    hb = add.get("headbreadth")
    r_head = (hb * CM / 2, hb * CM / 2) if hb else BASELINE["r_head"]

    # ------------------------------------------------------------------
    # Extract subject-specific lengths
    # ------------------------------------------------------------------
    L_foot    = max(FOOT_HEIGHT_MIN_M, min(FOOT_HEIGHT_MAX_M, foot_height_est))
    L_shank   = seg_len("Shank",      "L_shank")
    L_thigh_t = seg_len("Thigh",      "L_thigh")   # total, split below
    L_lower_t = seg_len("LowerTorso", "L_lower_torso")
    L_mid     = seg_len("MiddleTorso","L_middle_torso")
    L_upper_t = seg_len("UpperTorso", "L_upper_torso")
    L_uarm    = seg_len("UpperArm",   "L_upper_arm")
    L_larm    = seg_len("Forearm",    "L_lower_arm")
    L_hand    = seg_len("Hand",       "L_hand")
    L_head    = seg_len("Head",       "L_head")

    # Splits
    L_thigh       = L_thigh_t * THIGH_MAIN_FRAC
    L_thigh2      = L_thigh_t * THIGH_CAP_FRAC
    L_lower_torso  = L_lower_t * LOWER_TORSO_MAIN_FRAC
    L_lower_torso2 = L_lower_t * LOWER_TORSO_CAP_FRAC
    # upper_torso split (keep same ratio as baseline)
    L_upper_torso  = L_upper_t * 0.60
    L_upper_torso2 = L_upper_t * 0.40

    # ------------------------------------------------------------------
    # Build SegmentSpec dict
    # ------------------------------------------------------------------
    specs: Dict[str, SegmentSpec] = {}

    # Ankle / sole alignment in local X (0 = centered on foot axis).
    foot_heel_offset = 0.0

    # ── Right foot
    specs["r_foot"] = SegmentSpec(
        name="r_foot", shape="frustum", length=L_foot, res=RES,
        color=palette["foot"],
        r_bottom=r_bot_foot, r_top=r_top_foot, off_top=(foot_heel_offset, 0),
    )

    # ── Right shank
    specs["r_shank"] = SegmentSpec(
        name="r_shank", shape="frustum", length=L_shank, res=RES,
        color=palette["shank"],
        r_bottom=r_top_shank, r_top=r_bot_shank, off_top=(0, 0),
    )

    # ── Right thigh (main frustum)
    specs["r_thigh"] = SegmentSpec(
        name="r_thigh", shape="frustum", length=L_thigh, res=RES,
        color=palette["thigh"],
        r_bottom=r_top_thigh, r_top=r_bot_thigh, off_top=(0, 0),
    )

    # ── Right thigh2 (cone cap at hip)
    specs["r_thigh2"] = SegmentSpec(
        name="r_thigh2", shape="cone", length=L_thigh2, res=RES,
        color=palette["thigh2"],
        off_top=(r_top_thigh[0], 0), r=r_top_thigh,
    )

    # ── Left leg (mirror of right; l_thigh2 flips off_top Z)
    specs["l_foot"]   = copy.deepcopy(specs["r_foot"]);   specs["l_foot"].name   = "l_foot"
    specs["l_shank"]  = copy.deepcopy(specs["r_shank"]);  specs["l_shank"].name  = "l_shank"
    specs["l_thigh"]  = copy.deepcopy(specs["r_thigh"]);  specs["l_thigh"].name  = "l_thigh"
    specs["l_thigh2"] = copy.deepcopy(specs["r_thigh2"]); specs["l_thigh2"].name = "l_thigh2"
    specs["l_thigh2"].off_top = (-r_top_thigh[0], 0)     # mirror in X

    # ── Torso chain (bottom → top)
    specs["lower_torso2"] = SegmentSpec(
        name="lower_torso2", shape="cone", length=L_lower_torso2, res=RES,
        color=palette["lower_torso2"],
        off_top=(0, 0), r=r_bot_lower,
    )
    specs["lower_torso"] = SegmentSpec(
        name="lower_torso", shape="frustum", length=L_lower_torso, res=RES,
        color=palette["lower_torso"],
        r_bottom=r_bot_lower, r_top=r_top_lower, off_top=(0, 0),
    )
    specs["middle_torso"] = SegmentSpec(
        name="middle_torso", shape="frustum", length=L_mid, res=RES,
        color=palette["middle_torso"],
        r_bottom=r_top_lower, r_top=r_top_mid, off_top=(0, 0),
    )
    specs["upper_torso"] = SegmentSpec(
        name="upper_torso", shape="frustum", length=L_upper_torso, res=RES,
        color=palette["upper_torso"],
        r_bottom=r_top_mid, r_top=r_top_upper, off_top=(0, 0),
    )
    specs["upper_torso2"] = SegmentSpec(
        name="upper_torso2", shape="frustum", length=L_upper_torso2, res=RES,
        color=palette["upper_torso2"],
        r_bottom=r_top_upper, r_top=r_top_upper2, off_top=(0, 0),
    )

    # ── Right arm
    specs["r_upper_arm"] = SegmentSpec(
        name="r_upper_arm", shape="frustum", length=L_uarm, res=RES,
        color=palette["upper_arm"],
        r_bottom=r_shoulder, r_top=r_elbow, off_top=(0, 0),
    )
    specs["r_lower_arm"] = SegmentSpec(
        name="r_lower_arm", shape="frustum", length=L_larm, res=RES,
        color=palette["lower_arm"],
        r_bottom=r_elbow, r_top=r_wrist, off_top=(0, 0),
    )
    specs["r_hand"] = SegmentSpec(
        name="r_hand", shape="ellipsoid", length=L_hand, res=RES,
        color=palette["hand"], r=r_hand,
    )

    # ── Left arm (mirror)
    specs["l_upper_arm"] = copy.deepcopy(specs["r_upper_arm"]); specs["l_upper_arm"].name = "l_upper_arm"
    specs["l_lower_arm"] = copy.deepcopy(specs["r_lower_arm"]); specs["l_lower_arm"].name = "l_lower_arm"
    specs["l_hand"]      = copy.deepcopy(specs["r_hand"]);      specs["l_hand"].name      = "l_hand"

    # ── Head
    specs["head"] = SegmentSpec(
        name="head", shape="ellipsoid", length=L_head, res=RES,
        color=palette["head"], r=r_head,
    )

    return specs


# ---------------------------------------------------------------------------
# Convenience: load from JSON file path
# ---------------------------------------------------------------------------
def build_specs_from_json(json_path: str) -> Dict[str, SegmentSpec]:
    import json
    with open(json_path) as f:
        api = json.load(f)
    return build_specs_from_api(api)


# ---------------------------------------------------------------------------
# Quick sanity check (run directly: python api_to_poser_bridge.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json, sys

    path = sys.argv[1] if len(sys.argv) > 1 else "sample_segment_model.json"
    with open(path) as f:
        api = json.load(f)

    specs = build_specs_from_api(api)

    print(f"{'Segment':<18} {'shape':<10} {'length(m)':>10}  radii")
    print("-" * 65)
    for name, sp in specs.items():
        r_info = sp.r or sp.r_bottom or "—"
        print(f"{name:<18} {sp.shape:<10} {sp.length:>10.4f}  {r_info}")
