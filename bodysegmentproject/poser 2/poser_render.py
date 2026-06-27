#!/usr/bin/env python3
"""
Geometric humanoid poser — Python port of MATLAB fn_pose_anim2D_geometric_col / _front_col.

Pose vector layout (Simulink / MATLAB compatible)
-------------------------------------------------
- 20 segments in this exact order::

    r_foot, r_shank, r_thigh, r_thigh2, l_foot, l_shank, l_thigh, l_thigh2,
    lower_torso2, lower_torso, middle_torso, upper_torso, upper_torso2,
    r_upper_arm, r_lower_arm, r_hand, l_upper_arm, l_lower_arm, l_hand, head

- Per segment, 7 scalars: quaternion ``[qw, qx, qy, qz]`` then position ``[px, py, pz]`` (meters).
- **Python** 0-based index for segment ``i``: ``pose[7*i:7*i+4]``, ``pose[7*i+4:7*i+7]``.
- **MATLAB** uses 1-based columns: segment ``i`` starts at ``1 + 7*(i-1)``.

Export poses from MATLAB (example)::

    T = out.simout_anim_geometric.signals.values;  % N x 140
    writematrix(T, 'poses.csv');

Optional time vector::

    t = out.simout_anim_geometric.time;
    writematrix([t, T], 'poses_with_time.csv');

If the first column of a CSV is monotonically time-like, this CLI skips it when loading.

Coordinate system matches the MATLAB mesh builders: segment axis is **+Y** (proximal ``y=0``
toward distal ``y=length``); cross-section in **X/Z**.

The ``--demo`` pose is a heuristic T-pose (Z-up world, for sensible axes limits) for smoke testing only;
it does not reproduce Simulink. Use exported ``signals.values`` when you need identical poses to MATLAB.
"""

from __future__ import annotations

import argparse
import copy
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Literal, Optional, Sequence, Tuple

import numpy as np

if "--interactive" in sys.argv:
    os.environ.setdefault("MPLBACKEND", "TkAgg")

try:
    import matplotlib

    if not os.environ.get("MPLBACKEND"):
        matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import animation
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
except ImportError as e:  # pragma: no cover
    raise SystemExit("matplotlib is required. Install with: pip install matplotlib") from e

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SEGMENT_NAMES: Tuple[str, ...] = (
    "r_foot",
    "r_shank",
    "r_thigh",
    "r_thigh2",
    "l_foot",
    "l_shank",
    "l_thigh",
    "l_thigh2",
    "lower_torso2",
    "lower_torso",
    "middle_torso",
    "upper_torso",
    "upper_torso2",
    "r_upper_arm",
    "r_lower_arm",
    "r_hand",
    "l_upper_arm",
    "l_lower_arm",
    "l_hand",
    "head",
)

N_SEG = len(SEGMENT_NAMES)
POSE_DIM = 7 * N_SEG  # 140


@dataclass
class SegmentSpec:
    name: str
    shape: Literal["frustum", "cone", "ellipsoid"]
    length: float
    res: int
    color: np.ndarray
    r_bottom: Optional[Tuple[float, float]] = None
    r_top: Optional[Tuple[float, float]] = None
    off_top: Optional[Tuple[float, float]] = None
    r: Optional[Tuple[float, float]] = None


# ---------------------------------------------------------------------------
# Quaternion / rotation (wxyz matches MATLAB quat2rotm input as row)
# ---------------------------------------------------------------------------


def quat_wxyz_to_R(q: np.ndarray) -> np.ndarray:
    """Unit quaternion [qw,qx,qy,qz] -> 3x3 rotation matrix."""
    q = np.asarray(q, dtype=float).reshape(4)
    w, x, y, z = q
    n = w * w + x * x + y * y + z * z
    if n < 1e-12:
        return np.eye(3)
    s = 2.0 / n
    wx, wy, wz = s * w * x, s * w * y, s * w * z
    xx, xy, xz = s * x * x, s * x * y, s * x * z
    yy, yz, zz = s * y * y, s * y * z, s * z * z
    return np.array(
        [
            [1.0 - (yy + zz), xy - wz, xz + wy],
            [xy + wz, 1.0 - (xx + zz), yz - wx],
            [xz - wy, yz + wx, 1.0 - (xx + yy)],
        ]
    )


def R_to_quat_wxyz(R: np.ndarray) -> np.ndarray:
    """Rotation matrix -> unit quaternion [qw,qx,qy,qz]."""
    R = np.asarray(R, dtype=float).reshape(3, 3)
    t = np.trace(R)
    if t > 0:
        s = 0.5 / np.sqrt(t + 1.0)
        w = 0.25 / s
        x = (R[2, 1] - R[1, 2]) * s
        y = (R[0, 2] - R[2, 0]) * s
        z = (R[1, 0] - R[0, 1]) * s
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])
        w = (R[2, 1] - R[1, 2]) / s
        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
    elif R[1, 1] > R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])
        w = (R[0, 2] - R[2, 0]) / s
        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])
        w = (R[1, 0] - R[0, 1]) / s
        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
    q = np.array([w, x, y, z], dtype=float)
    return q / np.linalg.norm(q)


def transform_points(points: np.ndarray, q_wxyz: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Apply world rotation (wxyz) and translation to Nx3 points."""
    R = quat_wxyz_to_R(q_wxyz)
    pts = np.asarray(points, dtype=float).reshape(-1, 3)
    return (pts @ R.T) + np.asarray(p, dtype=float).reshape(1, 3)


# ---------------------------------------------------------------------------
# Segment catalog (geometric3D_healthy_color.m)
# ---------------------------------------------------------------------------


def _col(rgb255: Tuple[int, int, int]) -> np.ndarray:
    return np.array(rgb255, dtype=float) / 255.0


def build_segment_specs() -> Dict[str, SegmentSpec]:
    """Return segment specs keyed by name (matches geometric3D_healthy_color.m)."""
    res0 = 100
    col_feet = _col((240, 220, 220))
    col_shanks = _col((238, 210, 210))
    col_thighs = _col((235, 200, 200))
    col_thighs2 = _col((236, 205, 205))
    col_lower_torso = _col((232, 190, 190))
    col_lower_torso2 = _col((234, 195, 195))
    col_mid_torso = _col((230, 180, 180))
    col_upper_torso = _col((228, 170, 170))
    col_upper_torso2 = _col((229, 175, 175))
    col_upper_arm = _col((233, 188, 188))
    col_lower_arm = _col((236, 205, 205))
    col_hands = _col((240, 220, 220))
    col_head = _col((225, 165, 165))

    r_bottom_foot = (0.02, 0.045)
    r_top_foot = (0.01, 0.04)
    r_top_shank = (0.06, 0.05)
    r_top_thigh = (0.09, 0.0925)
    # Thigh: hip (y=0) wide -> knee (y=L) slim; knee radius matches shank knee.
    # Shank: knee (y=0) wide -> ankle (y=L) slim; ankle matches foot top.

    specs: Dict[str, SegmentSpec] = {}

    def add(spec: SegmentSpec) -> None:
        specs[spec.name] = spec

    add(
        SegmentSpec(
            "r_foot",
            "frustum",
            0.21,
            res0,
            col_feet,
            r_bottom=r_bottom_foot,
            r_top=r_top_foot,
            off_top=(0.0, 0.0),
        )
    )
    add(
        SegmentSpec(
            "r_shank",
            "frustum",
            0.45,
            res0,
            col_shanks,
            r_bottom=r_top_shank,
            r_top=r_bottom_foot,
            off_top=(0.0, 0.0),
        )
    )
    add(
        SegmentSpec(
            "r_thigh",
            "frustum",
            0.45,
            res0,
            col_thighs,
            r_bottom=r_top_thigh,
            r_top=r_top_shank,
            off_top=(0.0, 0.0),
        )
    )
    add(
        SegmentSpec(
            "r_thigh2",
            "cone",
            0.12,
            res0,
            col_thighs2,
            r=r_top_thigh,
            off_top=(0.0, r_top_thigh[1]),
        )
    )

    r_bottom_lower = (0.14, 0.18)
    r_top_lower = (0.13, 0.17)
    r_top_mid = (0.13, 0.19)
    r_top_upper = (0.12, 0.22)
    r_top_upper2 = (0.05, 0.08)

    add(
        SegmentSpec(
            "lower_torso",
            "frustum",
            0.18,
            res0,
            col_lower_torso,
            r_bottom=r_bottom_lower,
            r_top=r_top_lower,
            off_top=(0.0, 0.0),
        )
    )
    add(
        SegmentSpec(
            "lower_torso2",
            "cone",
            0.12,
            res0,
            col_lower_torso2,
            r=r_bottom_lower,
            off_top=(0.0, 0.0),
        )
    )
    add(
        SegmentSpec(
            "middle_torso",
            "frustum",
            0.25,
            res0,
            col_mid_torso,
            r_bottom=r_top_lower,
            r_top=r_top_mid,
            off_top=(r_top_mid[0] - r_top_lower[0], 0.0),
        )
    )
    add(
        SegmentSpec(
            "upper_torso",
            "frustum",
            0.18,
            res0,
            col_upper_torso,
            r_bottom=r_top_mid,
            r_top=r_top_upper,
            off_top=(0.0, 0.0),
        )
    )
    add(
        SegmentSpec(
            "upper_torso2",
            "frustum",
            0.12,
            res0,
            col_upper_torso2,
            r_bottom=r_top_upper,
            r_top=r_top_upper2,
            off_top=(0.0, 0.0),
        )
    )

    # Upper arm: shoulder (y=0) a bit wider than elbow (y=length).
    r_shoulder = (0.04, 0.04)
    r_elbow = (0.03, 0.03)
    add(
        SegmentSpec(
            "r_upper_arm",
            "frustum",
            0.30,
            res0,
            col_upper_arm,
            r_bottom=r_shoulder,
            r_top=r_elbow,
            off_top=(0.0, 0.0),
        )
    )
    add(
        SegmentSpec(
            "r_lower_arm",
            "frustum",
            0.28,
            res0,
            col_lower_arm,
            r_bottom=r_elbow,
            r_top=(0.02, 0.02),
            off_top=(0.0, 0.0),
        )
    )
    add(
        SegmentSpec(
            "r_hand",
            "ellipsoid",
            0.08,
            res0,
            col_hands,
            r=(0.035, 0.035),
        )
    )
    add(
        SegmentSpec(
            "head",
            "ellipsoid",
            0.25,
            res0,
            col_head,
            r=(0.09, 0.10),
        )
    )

    # Left side: deep-copy right limb/torso symmetric parts
    for name_r, name_l in (
        ("r_foot", "l_foot"),
        ("r_shank", "l_shank"),
        ("r_thigh", "l_thigh"),
        ("r_thigh2", "l_thigh2"),
        ("r_upper_arm", "l_upper_arm"),
        ("r_lower_arm", "l_lower_arm"),
        ("r_hand", "l_hand"),
    ):
        sp = copy.deepcopy(specs[name_r])
        sp.name = name_l
        if name_l == "l_thigh2" and sp.off_top is not None:
            ox, oz = sp.off_top
            sp.off_top = (ox, -oz)
        specs[name_l] = sp

    return specs


DEFAULT_SUBJECT_HEIGHT_M = 1.8
SHOULDER_HALF_WIDTH = 0.22


def hip_half_width_m(subject_height_m: float) -> float:
    """
    Half of the distance between hip joints (meters).

    Full inter-hip width = 0.2 * subject_height / 1.8 (0.2 m at 1.8 m tall).
    """
    return 0.5 * (0.22 * float(subject_height_m) / 1.8)


# ---------------------------------------------------------------------------
# Mesh generation (MATLAB Create*Objects)
# ---------------------------------------------------------------------------


def mesh_frustum(spec: SegmentSpec) -> List[Tuple[np.ndarray, np.ndarray]]:
    """Return list of (vertices, faces) for side, bottom cap, top cap."""
    assert spec.r_bottom and spec.r_top and spec.off_top is not None
    h = spec.length
    rb1, rb2 = spec.r_bottom
    rt1, rt2 = spec.r_top
    ox, oz = spec.off_top
    res = spec.res
    th = np.linspace(0, 2 * np.pi, res, endpoint=False)
    xb = rb1 * np.cos(th)
    zb = rb2 * np.sin(th)
    yb = np.zeros(res)
    xt = ox + rt1 * np.cos(th)
    zt = oz + rt2 * np.sin(th)
    yt = np.full(res, h)

    # Side: two rings, 2*res verts
    side_v = np.vstack(
        [np.column_stack([xb, yb, zb]), np.column_stack([xt, yt, zt])]
    )
    faces_s = []
    for i in range(res):
        j = (i + 1) % res
        faces_s.append([i, j, j + res])
        faces_s.append([i, j + res, i + res])
    side = (side_v, np.array(faces_s, dtype=np.int32))

    # Bottom cap (center + ring)
    verts_b = np.vstack([np.array([[0.0, 0.0, 0.0]]), np.column_stack([xb, yb, zb])])
    faces_b = []
    c = 0
    for i in range(res):
        j = (i + 1) % res
        faces_b.append([c, 1 + i, 1 + j])
    bottom = (verts_b, np.array(faces_b, dtype=np.int32))

    # Top cap
    center_top = np.array([[ox, h, oz]])
    verts_t = np.vstack([center_top, np.column_stack([xt, yt, zt])])
    faces_t = []
    c = 0
    for i in range(res):
        j = (i + 1) % res
        faces_t.append([c, 1 + j, 1 + i])
    top = (verts_t, np.array(faces_t, dtype=np.int32))

    return [side, bottom, top]


def mesh_cone(spec: SegmentSpec) -> List[Tuple[np.ndarray, np.ndarray]]:
    assert spec.r and spec.off_top is not None
    h = spec.length
    r1, r2 = spec.r
    ox, oz = spec.off_top
    res = spec.res
    th = np.linspace(0, 2 * np.pi, res, endpoint=False)
    xb = r1 * np.cos(th)
    zb = r2 * np.sin(th)
    yb = np.zeros(res)
    tip = np.array([[ox, h, oz]])
    side_v = np.vstack([np.column_stack([xb, yb, zb]), tip])
    tip_i = res
    faces_s = []
    for i in range(res):
        j = (i + 1) % res
        faces_s.append([i, j, tip_i])
    side = (side_v, np.array(faces_s, dtype=np.int32))

    verts_b = np.vstack([np.array([[0.0, 0.0, 0.0]]), np.column_stack([xb, yb, zb])])
    faces_b = []
    for i in range(res):
        j = (i + 1) % res
        faces_b.append([0, 1 + i, 1 + j])
    bottom = (verts_b, np.array(faces_b, dtype=np.int32))
    return [side, bottom]


def mesh_ellipsoid(spec: SegmentSpec) -> List[Tuple[np.ndarray, np.ndarray]]:
    assert spec.r is not None
    length = spec.length
    r1, r2 = spec.r
    res = spec.res
    theta = np.linspace(0, 2 * np.pi, res, endpoint=False)
    phi = np.linspace(0, np.pi, max(3, res // 2))
    tg, pg = np.meshgrid(theta, phi, indexing="xy")
    x = r1 * np.sin(pg) * np.cos(tg)
    z = r2 * np.sin(pg) * np.sin(tg)
    y = (length / 2.0) * np.cos(pg) + (length / 2.0)
    verts = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    nt = len(theta)
    np_ = len(phi)
    faces = []
    for i in range(np_ - 1):
        for j in range(nt):
            jn = (j + 1) % nt
            i0 = i * nt + j
            i1 = i * nt + jn
            i2 = (i + 1) * nt + jn
            i3 = (i + 1) * nt + j
            faces.append([i0, i1, i2])
            faces.append([i0, i2, i3])
    return [(verts, np.array(faces, dtype=np.int32))]


def meshes_for_spec(spec: SegmentSpec) -> List[Tuple[np.ndarray, np.ndarray]]:
    if spec.shape == "frustum":
        return mesh_frustum(spec)
    if spec.shape == "cone":
        return mesh_cone(spec)
    if spec.shape == "ellipsoid":
        return mesh_ellipsoid(spec)
    raise ValueError(f"Unknown shape {spec.shape}")


def build_all_meshes(specs: Dict[str, SegmentSpec]) -> Dict[str, List[Tuple[np.ndarray, np.ndarray]]]:
    return {name: meshes_for_spec(specs[name]) for name in SEGMENT_NAMES}


# ---------------------------------------------------------------------------
# Pose packing / loading
# ---------------------------------------------------------------------------


def pack_pose(transforms: Dict[str, Tuple[np.ndarray, np.ndarray]]) -> np.ndarray:
    """transforms[name] = (q_wxyz (4,), p (3,)) -> flat (140,) array."""
    out = np.zeros(POSE_DIM)
    for i, name in enumerate(SEGMENT_NAMES):
        q, p = transforms[name]
        out[7 * i : 7 * i + 4] = np.asarray(q, dtype=float).reshape(4)
        out[7 * i + 4 : 7 * i + 7] = np.asarray(p, dtype=float).reshape(3)
    return out


def unpack_pose_row(row: np.ndarray) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    row = np.asarray(row, dtype=float).reshape(POSE_DIM)
    d: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}
    for i, name in enumerate(SEGMENT_NAMES):
        d[name] = (row[7 * i : 7 * i + 4].copy(), row[7 * i + 4 : 7 * i + 7].copy())
    return d


def _maybe_skip_time_column(data: np.ndarray) -> np.ndarray:
    """If 141 columns and first col looks like time, drop it."""
    if data.shape[1] == POSE_DIM + 1:
        return data[:, 1:]
    if data.shape[1] == POSE_DIM:
        return data
    raise ValueError(
        f"Expected {POSE_DIM} or {POSE_DIM + 1} columns per row, got {data.shape[1]}"
    )


def load_pose_csv(path: str) -> np.ndarray:
    try:
        data = np.loadtxt(path, delimiter=",", dtype=float, ndmin=2)
    except ValueError:
        data = np.loadtxt(path, dtype=float, ndmin=2)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    return _maybe_skip_time_column(data)


def load_pose_npy(path: str) -> np.ndarray:
    arr = np.load(path)
    arr = np.asarray(arr, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    return _maybe_skip_time_column(arr)


# ---------------------------------------------------------------------------
# Heuristic demo T-pose
# ---------------------------------------------------------------------------


def _Rx(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def _Rz(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


def _qp(R: np.ndarray, p: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    return (R_to_quat_wxyz(R), np.asarray(p, dtype=float))


def demo_tpose_transforms(
    specs: Dict[str, SegmentSpec],
    subject_height_m: float = DEFAULT_SUBJECT_HEIGHT_M,
) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    """
    Approximate standing T-pose. Segment mesh axis is local +Y (MATLAB); we use world +Z vertical
    to match ``axis([.., -0.2, 1.8])`` style limits in the MATLAB animator.
    """
    Llt = specs["lower_torso"].length
    Lmid = specs["middle_torso"].length
    Lup = specs["upper_torso"].length
    Luk = specs["upper_torso2"].length

    # Maps segment local +Y to world +Z (standing trunk along Z)
    R_up = _Rx(np.pi / 2)
    pelvis = np.array([0.0, 0.0, 0.08], dtype=float)

    out: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}

    # Trunk chain along +Z
    p = pelvis.copy()
    out["lower_torso"] = _qp(R_up, p)
    p = p + R_up @ np.array([0.0, Llt, 0.0])
    out["middle_torso"] = _qp(R_up, p)
    p = p + R_up @ np.array([0.0, Lmid, 0.0])
    out["upper_torso"] = _qp(R_up, p)
    p = p + R_up @ np.array([0.0, Lup, 0.0])
    out["upper_torso2"] = _qp(R_up, p)
    p_neck = p + R_up @ np.array([0.0, Luk, 0.0])
    out["head"] = _qp(R_up, p_neck)

    # Pelvis-bottom cone: local +Y -> world -Z
    R_down = _Rx(-np.pi / 2)
    out["lower_torso2"] = _qp(R_down, pelvis)

    # Legs: local +Y -> world -Z
    # Attach hip joints to the bottom of lower_torso2 (avoids thigh/waist overlap).
    p_hips = pelvis + R_down @ np.array([0.0, specs["lower_torso2"].length, 0.0])
    hip_dx = hip_half_width_m(subject_height_m)
    hip_r = p_hips + np.array([hip_dx, 0.0, 0.0])
    hip_l = p_hips + np.array([-hip_dx, 0.0, 0.0])
    R_leg = R_down
    # Keep thigh/shank vertical, but pitch feet forward from the ankle.
    R_foot = R_leg @ _Rx(np.pi / 2)
    Lth = specs["r_thigh"].length
    Lsh = specs["r_shank"].length

    out["r_thigh"] = _qp(R_leg, hip_r)
    knee_r = hip_r + R_leg @ np.array([0.0, Lth, 0.0])
    out["r_shank"] = _qp(R_leg, knee_r)
    ankle_r = knee_r + R_leg @ np.array([0.0, Lsh, 0.0])
    out["r_foot"] = _qp(R_foot, ankle_r)
    # Thigh top cone attaches upward into lower torso.
    out["r_thigh2"] = _qp(R_up, hip_r)

    out["l_thigh"] = _qp(R_leg, hip_l)
    knee_l = hip_l + R_leg @ np.array([0.0, Lth, 0.0])
    out["l_shank"] = _qp(R_leg, knee_l)
    ankle_l = knee_l + R_leg @ np.array([0.0, Lsh, 0.0])
    out["l_foot"] = _qp(R_foot, ankle_l)
    out["l_thigh2"] = _qp(R_up, hip_l)

    # Arms: local +Y -> world ±X (T-pose); Rz(-pi/2) maps e_y -> +e_x
    # Attach both arms to upper_torso outer side (no lateral gap).
    R_arm_r = _Rz(-np.pi / 2)
    R_arm_l = _Rz(np.pi / 2)
    shoulder_anchor = p
    upper_torso_spec = specs["upper_torso"]
    torso_half_width = upper_torso_spec.r_top[0] if upper_torso_spec.r_top is not None else SHOULDER_HALF_WIDTH
    sh_r = shoulder_anchor + np.array([torso_half_width, 0.0, 0.0])
    sh_l = shoulder_anchor + np.array([-torso_half_width, 0.0, 0.0])
    Lua = specs["r_upper_arm"].length
    Lla = specs["r_lower_arm"].length

    out["r_upper_arm"] = _qp(R_arm_r, sh_r)
    el_r = sh_r + R_arm_r @ np.array([0.0, Lua, 0.0])
    out["r_lower_arm"] = _qp(R_arm_r, el_r)
    wr_r = el_r + R_arm_r @ np.array([0.0, Lla, 0.0])
    out["r_hand"] = _qp(R_arm_r, wr_r)

    out["l_upper_arm"] = _qp(R_arm_l, sh_l)
    el_l = sh_l + R_arm_l @ np.array([0.0, Lua, 0.0])
    out["l_lower_arm"] = _qp(R_arm_l, el_l)
    wr_l = el_l + R_arm_l @ np.array([0.0, Lla, 0.0])
    out["l_hand"] = _qp(R_arm_l, wr_l)

    return out


def demo_tpose_pack(
    specs: Dict[str, SegmentSpec],
    subject_height_m: float = DEFAULT_SUBJECT_HEIGHT_M,
) -> np.ndarray:
    return pack_pose(demo_tpose_transforms(specs, subject_height_m))


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

ViewName = Literal["side_view", "front", "orbit"]


def _axis_limits() -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
    return ((-0.6, 0.7), (-0.5, 0.5), (-0.2, 1.8))


def _axis_box_aspect(
    xlim: Tuple[float, float], ylim: Tuple[float, float], zlim: Tuple[float, float]
) -> Tuple[float, float, float]:
    """Match 3D box aspect to axis spans to avoid visual squashing."""
    return (xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0])


def apply_view_mpl(ax: plt.Axes, view: ViewName) -> None:
    """Set camera for side view, front, or a default orbit angle (user can drag to rotate)."""
    if view == "side_view":
        elev, azim = 0.0, 180.0
    elif view == "front":
        elev, azim = 0.0, -90.0
    else:
        elev, azim = 18.0, -55.0
    try:
        ax.view_init(elev=elev, azim=azim, vertical_axis="z")
    except TypeError:
        ax.view_init(elev=elev, azim=azim)


def _compute_pose_limits(
    tr: Dict[str, Tuple[np.ndarray, np.ndarray]],
    meshes: Dict[str, List[Tuple[np.ndarray, np.ndarray]]],
    pad_ratio: float = 0.08,
) -> Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]:
    """Compute axis limits from transformed mesh vertices with padding."""
    mins = np.array([np.inf, np.inf, np.inf], dtype=float)
    maxs = np.array([-np.inf, -np.inf, -np.inf], dtype=float)

    for name in SEGMENT_NAMES:
        q, p = tr[name]
        for verts, _faces in meshes[name]:
            v_w = transform_points(verts, q, p)
            mins = np.minimum(mins, np.min(v_w, axis=0))
            maxs = np.maximum(maxs, np.max(v_w, axis=0))

    spans = np.maximum(maxs - mins, 1e-6)
    pad = spans * pad_ratio
    mins -= pad
    maxs += pad
    return ((mins[0], maxs[0]), (mins[1], maxs[1]), (mins[2], maxs[2]))


def render_pose_to_figure(
    pose_row: np.ndarray,
    specs: Dict[str, SegmentSpec],
    meshes: Dict[str, List[Tuple[np.ndarray, np.ndarray]]],
    view: ViewName,
    dpi: int = 120,
    figsize: Tuple[float, float] = (8.0, 8.0),
) -> plt.Figure:
    pose_row = np.asarray(pose_row, dtype=float).reshape(POSE_DIM)
    tr = unpack_pose_row(pose_row)

    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor="white")
    ax = fig.add_subplot(111, projection="3d", facecolor="white")
    # Orthographic projection reduces perspective-induced apparent overlap/asymmetry.
    try:
        ax.set_proj_type("ortho")
    except Exception:
        pass
    xlim, ylim, zlim = _compute_pose_limits(tr, meshes)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_zlim(zlim)
    ax.set_axis_off()
    ax.set_box_aspect(_axis_box_aspect(xlim, ylim, zlim))

    light_dir = np.array([0.55, 0.35, 0.76], dtype=float)
    light_dir /= np.linalg.norm(light_dir)

    for name in SEGMENT_NAMES:
        q, p = tr[name]
        base_rgb = specs[name].color
        for verts, faces in meshes[name]:
            v_w = transform_points(verts, q, p)
            polys = [v_w[idx] for idx in faces]
            cols = []
            for tri in polys:
                n = np.cross(tri[1] - tri[0], tri[2] - tri[0])
                ln = np.linalg.norm(n)
                if ln < 1e-12:
                    shade = 1.0
                else:
                    n = n / ln
                    shade = 0.35 + 0.65 * max(0.0, float(np.dot(n, light_dir)))
                rgb = np.clip(base_rgb * shade, 0.0, 1.0)
                cols.append(tuple(rgb))
            pc = Poly3DCollection(polys, facecolors=cols, edgecolors="none", linewidths=0)
            ax.add_collection3d(pc)

    apply_view_mpl(ax, view)
    fig.tight_layout(pad=0)
    return fig


def save_figure(fig: plt.Figure, path: str) -> None:
    fig.savefig(path, bbox_inches="tight", facecolor="white", pad_inches=0.02)
    plt.close(fig)


def show_figure(fig: plt.Figure, block: bool = True) -> None:
    """Open an interactive window (rotate/zoom with mouse; close window to continue)."""
    manager = getattr(fig.canvas, "manager", None)
    if manager is not None and getattr(manager, "set_window_title", None):
        manager.set_window_title("Body segment model — drag to rotate, scroll to zoom")
    print(
        "Interactive viewer open: drag to rotate, right-drag or scroll to zoom, "
        "close the window to exit.",
        file=sys.stderr,
    )
    plt.show(block=block)


def render_animation_gif(
    poses: np.ndarray,
    specs: Dict[str, SegmentSpec],
    meshes: Dict[str, List[Tuple[np.ndarray, np.ndarray]]],
    view: ViewName,
    out_path: str,
    fps: int = 10,
) -> None:
    poses = np.asarray(poses, dtype=float)
    if poses.ndim == 1:
        poses = poses.reshape(1, -1)

    fig = plt.figure(figsize=(8, 8), dpi=100, facecolor="white")
    ax = fig.add_subplot(111, projection="3d", facecolor="white")
    try:
        ax.set_proj_type("ortho")
    except Exception:
        pass
    light_dir = np.array([0.55, 0.35, 0.76], dtype=float)
    light_dir /= np.linalg.norm(light_dir)

    def draw_frame(frame: int) -> None:
        row = poses[frame % len(poses)].reshape(POSE_DIM)
        tr = unpack_pose_row(row)
        xlim, ylim, zlim = _compute_pose_limits(tr, meshes)

        ax.clear()
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.set_zlim(zlim)
        ax.set_axis_off()
        ax.set_box_aspect(_axis_box_aspect(xlim, ylim, zlim))
        for name in SEGMENT_NAMES:
            q, p = tr[name]
            base_rgb = specs[name].color
            for verts, faces in meshes[name]:
                v_w = transform_points(verts, q, p)
                polys = [v_w[i] for i in faces]
                cols = []
                for tri in polys:
                    n = np.cross(tri[1] - tri[0], tri[2] - tri[0])
                    ln = np.linalg.norm(n)
                    if ln < 1e-12:
                        shade = 1.0
                    else:
                        n = n / ln
                        shade = 0.35 + 0.65 * max(0.0, float(np.dot(n, light_dir)))
                    rgb = np.clip(base_rgb * shade, 0.0, 1.0)
                    cols.append(tuple(rgb))
                pc = Poly3DCollection(
                    polys, facecolors=cols, edgecolors="none", linewidths=0
                )
                ax.add_collection3d(pc)
        apply_view_mpl(ax, view)

    anim = animation.FuncAnimation(
        fig,
        draw_frame,
        frames=len(poses),
        interval=max(1, 1000 // max(1, fps)),
        blit=False,
    )
    anim.save(out_path, writer=animation.PillowWriter(fps=fps))
    plt.close(fig)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _view_file_suffix(view: ViewName) -> str:
    """Filename suffix for a rendered view (front -> front_view on disk)."""
    if view == "front":
        return "front_view"
    return view


def resolve_png_outputs(output: str, views: List[ViewName]) -> List[Tuple[ViewName, str]]:
    if len(views) == 1:
        v = views[0]
        if output.lower().endswith(".png"):
            return [(v, output)]
        return [(v, f"{output}_{_view_file_suffix(v)}.png")]
    stem = output[:-4] if output.lower().endswith(".png") else output
    return [(v, f"{stem}_{_view_file_suffix(v)}.png") for v in views]


def resolve_gif_path(gif_arg: str, view: ViewName, multi_view: bool) -> str:
    p = Path(gif_arg)
    if p.suffix.lower() != ".gif":
        p = p.with_suffix(".gif")
    if multi_view:
        return str(p.with_name(f"{p.stem}_{_view_file_suffix(view)}{p.suffix}"))
    return str(p)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Pose columns: 140 values = 20 segments × (qw,qx,qy,qz,px,py,pz). "
            "Segment order is listed in the module docstring."
        ),
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--demo", action="store_true", help="Use built-in heuristic T-pose")
    src.add_argument("--pose-csv", type=str, metavar="PATH", help="CSV with one pose row per line")
    src.add_argument("--pose-npy", type=str, metavar="PATH", help="NumPy array shape (N,140) or (140,)")

    p.add_argument(
        "--frame",
        type=int,
        default=0,
        help="Row index for CSV/npy when not making a GIF (default: 0)",
    )
    p.add_argument(
        "--view",
        choices=["side_view", "front", "both"],
        default="both",
        help="Camera view: side view, front, or both (default: both)",
    )
    p.add_argument(
        "--output",
        type=str,
        default="out",
        metavar="PREFIX",
        help="Output path prefix (default: out). Adds _side_view.png / _front_view.png",
    )
    p.add_argument("--dpi", type=int, default=150, help="Figure DPI for PNG (default: 150)")
    p.add_argument(
        "--gif",
        type=str,
        default=None,
        metavar="PATH.gif",
        help="If set with multi-row pose data, write animated GIF to this path",
    )
    p.add_argument("--fps", type=int, default=10, help="FPS for --gif (default: 10)")
    p.add_argument(
        "--interactive",
        action="store_true",
        help="Open a rotatable 3D window instead of only writing PNGs (orbit view)",
    )
    p.add_argument(
        "--height",
        type=float,
        default=DEFAULT_SUBJECT_HEIGHT_M,
        metavar="M",
        help=(
            "Subject height in meters for --demo only: hip joint half-width = "
            "0.1*height/1.8 (full width 0.2 m at 1.8 m). Default: %(default)s"
        ),
    )
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    specs = build_segment_specs()
    meshes = build_all_meshes(specs)

    if args.demo:
        pose_data = demo_tpose_pack(specs, args.height).reshape(1, POSE_DIM)
    elif args.pose_csv:
        pose_data = load_pose_csv(args.pose_csv)
    else:
        pose_data = load_pose_npy(args.pose_npy)

    if args.gif:
        if pose_data.shape[0] < 2:
            print(
                "Warning: GIF requested with a single pose; animation repeats one frame.",
                file=sys.stderr,
            )
        multi = args.view == "both"
        for v in ("side_view", "front"):
            if args.view in (v, "both"):
                gif_path = resolve_gif_path(args.gif, v, multi)
                render_animation_gif(pose_data, specs, meshes, v, gif_path, fps=args.fps)
                print(f"Wrote {gif_path}")
        return 0

    frame = int(args.frame)
    if frame < 0 or frame >= pose_data.shape[0]:
        raise SystemExit(f"frame {frame} out of range [0, {pose_data.shape[0] - 1}]")

    row = pose_data[frame]

    if args.interactive:
        fig = render_pose_to_figure(row, specs, meshes, "orbit", dpi=args.dpi)
        show_figure(fig)
        return 0

    views: List[ViewName] = (
        ["side_view", "front"] if args.view == "both" else [args.view]  # type: ignore[list-item]
    )

    for v, out_path in resolve_png_outputs(args.output, views):
        fig = render_pose_to_figure(row, specs, meshes, v, dpi=args.dpi)
        save_figure(fig, out_path)
        print(f"Wrote {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
