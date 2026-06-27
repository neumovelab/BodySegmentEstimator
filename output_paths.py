"""Helpers for unique per-run output directory names."""

from __future__ import annotations

import os
from datetime import datetime


def run_timestamp(when: datetime | None = None) -> str:
    """Compact timestamp tag, e.g. 20260527_143052."""
    return (when or datetime.now()).strftime("%Y%m%d_%H%M%S")


def timestamped_dir(dir_path: str, when: datetime | None = None) -> str:
    """
    Prefix the leaf folder name with a run timestamp (sorts chronologically).

    output/baseline_male_120kg_1p8m -> output/20260527_143052_baseline_male_120kg_1p8m
    """
    ts = run_timestamp(when)
    norm = os.path.normpath(dir_path)
    parent, base = os.path.split(norm)
    if not base:
        base = "output"
        parent = norm
    stamped = f"{ts}_{base}"
    return stamped if not parent else os.path.join(parent, stamped)


def _num_tag(value: float, suffix: str = "") -> str:
    s = f"{float(value):.2f}".rstrip("0").rstrip(".").replace(".", "p")
    return f"{s}{suffix}"


def default_run_folder_name(mode: str, data: dict) -> str:
    """Folder name for one run: e.g. baseline_male_120kg_1p8m."""
    sex = str(data.get("sex", "subject")).lower()
    weight = _num_tag(float(data.get("weight", 0.0)), "kg")
    height = _num_tag(float(data.get("height", 0.0)), "m")
    return f"{mode}_{sex}_{weight}_{height}"


def resolve_run_output_dir(
    mode: str,
    data: dict,
    output_dir: str | None,
    *,
    output_root: str,
    stamp: bool = True,
    when: datetime | None = None,
) -> str:
    """
    Resolve the directory for a single run.

    Default: output/<YYYYMMDD_HHMMSS>_<mode>_<sex>_<weight>_<height>/
    Explicit --output-dir uses that path (timestamped unless disabled).
    --output-dir output is treated like the default (run folder inside output/).
    """
    folder = default_run_folder_name(mode, data)
    root = os.path.abspath(output_root)
    if output_dir is None:
        base = os.path.join(root, folder)
    else:
        requested = os.path.abspath(output_dir)
        if requested == root:
            base = os.path.join(root, folder)
        else:
            base = requested
    if stamp:
        base = timestamped_dir(base, when=when)
    return base
