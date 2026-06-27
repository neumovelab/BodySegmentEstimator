"""
examples.py – CLI/examples for Body Inertia Library + Poser visualisation.

Runs a subject measurement preset through the inertia API, builds a
personalised body mesh via api_to_poser_bridge, and renders PNG(s) with
poser_render.py — all in pure Python, no MATLAB needed.

    python examples.py                                 # baseline → ./output/<timestamp>_baseline_.../
    python examples.py custom --height 1.75 --weight 80
    python examples.py custom --height 1.74 --weight 82 --sex male \
        --param thigh=0.50 --param waist_circumference=0.96 --param chest_circumference=1.04 \
        --output-dir ./runs/custom --view both --dpi 200
    python examples.py shape --view front --output-dir ./runs
    python examples.py baseline --gif walk.gif --pose-csv poses.npy
    python examples.py custom --no-image
"""

import os
import sys

# Interactive 3D viewer needs a GUI backend before matplotlib is imported in poser_render.
if "--interactive" in sys.argv:
    os.environ.setdefault("MPLBACKEND", "TkAgg")

from bodysegmentproject import SubjectMeasures
from api_to_poser_bridge import build_specs_from_api
from output_paths import resolve_run_output_dir

# poser_render lives under bodysegmentproject/poser 2/ (folder name has a space).
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_OUTPUT_DIR = os.path.join(_REPO_ROOT, "output")
_DEFAULT_EXPORT_STEM = "out"
sys.path.insert(0, os.path.join(_REPO_ROOT, "bodysegmentproject", "poser 2"))

from poser_render import (
    build_all_meshes,
    demo_tpose_pack,
    load_pose_csv,
    load_pose_npy,
    render_pose_to_figure,
    render_animation_gif,
    save_figure,
    show_figure,
    resolve_png_outputs,
    resolve_gif_path,
    POSE_DIM,
)

import argparse


# ---------------------------------------------------------------------------
# Presets
# ---------------------------------------------------------------------------

PRESETS = {
    "baseline": {
        "unit_measure": "SI",
        "height": 1.80,
        "weight": 120,
        "sex": "male",
        "output_file": "out.xlsx",
    },
    "custom": {
        "unit_measure": "SI",
        "height": 1.80,
        "weight": 120,
        "sex": "male",
        "thigh": 0.46,
        "waist_circumference": 0.92,
        "chest_circumference": 1.05,
        "output_file": "out.xlsx",
    },
    "shape": {
        "unit_measure": "SI",
        "height": 1.80,
        "weight": 120,
        "sex": "male",
        "hip_circumference": 1.00,
        "waist_circumference": 0.88,
        "output_file": "out.xlsx",
    },
}


# ---------------------------------------------------------------------------
# Core run
# ---------------------------------------------------------------------------

def _under_dir(path: str, out_dir: str) -> str:
    """Place run artifacts under out_dir."""
    if os.path.isabs(path):
        path = os.path.basename(path)
    return os.path.normpath(os.path.join(out_dir, path))


def run(mode, overrides, view="both", output="out",
        gif=None, fps=10, pose_csv=None, pose_npy=None, frame=0, dpi=150,
        output_dir=None, stamp_output_dir=True, interactive=False,
        save_with_interactive=False):
    """
    1. Run inertia API  → segment dict
    2. Build SegmentSpec dict via bridge
    3. Build meshes
    4. Render PNG (and optionally GIF)
    """
    data = {**PRESETS[mode], **overrides}
    generate_image = bool(data.pop("generate_image", True))
    out_dir = resolve_run_output_dir(
        mode,
        data,
        output_dir,
        output_root=_DEFAULT_OUTPUT_DIR,
        stamp=stamp_output_dir,
    )
    os.makedirs(out_dir, exist_ok=True)
    print(f"All outputs → {out_dir}")

    # ── 1. API + file exports
    export_seed = data.get("output_file", f"{_DEFAULT_EXPORT_STEM}.xlsx")
    export_stem = os.path.splitext(os.path.basename(export_seed))[0] or _DEFAULT_EXPORT_STEM
    export_paths = {
        "xlsx": os.path.join(out_dir, f"{export_stem}.xlsx"),
        "json": os.path.join(out_dir, f"{export_stem}.json"),
        "mat":  os.path.join(out_dir, f"{export_stem}.mat"),
        "pkl":  os.path.join(out_dir, f"{export_stem}.pkl"),
    }

    sm = SubjectMeasures({**data, "output_file": export_paths["xlsx"]})
    sm.GetSubjectMeasures()
    sm.create_file()  # xlsx

    for ext in ("json", "mat", "pkl"):
        sm.data["output_file"] = export_paths[ext]
        sm.create_file()

    api_dict = sm.SegmentModel.to_dict()
    print(
        "API done → {} (height={} m, weight={} kg, sex={})".format(
            out_dir, data["height"], data["weight"], data["sex"]
        )
    )
    print("Wrote {}".format(export_paths["xlsx"]))
    print("Wrote {}".format(export_paths["json"]))
    print("Wrote {}".format(export_paths["mat"]))
    print("Wrote {}".format(export_paths["pkl"]))

    # ── 2. Bridge: personalised SegmentSpec dict
    specs = build_specs_from_api(api_dict, sex=data.get("sex"))
    print("Bridge done → {} segment specs built".format(len(specs)))

    if not generate_image and not interactive:
        print("Image generation disabled (generate_image=False); skipping poser render.")
        return data

    # ── 3. Meshes
    meshes = build_all_meshes(specs)

    # ── 4. Pose
    if pose_csv:
        pose_data = load_pose_csv(pose_csv)
    elif pose_npy:
        pose_data = load_pose_npy(pose_npy)
    else:
        # Default: heuristic T-pose scaled to this subject's height
        pose_data = demo_tpose_pack(specs, data["height"]).reshape(1, POSE_DIM)

    if frame < 0 or frame >= pose_data.shape[0]:
        raise SystemExit(f"frame {frame} out of range [0, {pose_data.shape[0]-1}]")
    row = pose_data[frame]

    # ── 5. Interactive 3D viewer
    if interactive:
        if gif:
            raise SystemExit("--interactive cannot be used with --gif")
        fig = render_pose_to_figure(row, specs, meshes, "orbit", dpi=dpi)
        if save_with_interactive:
            views = ["side_view", "front"] if view == "both" else [view]
            png_prefix = _under_dir(output, out_dir)
            for v, out_path in resolve_png_outputs(png_prefix, views):
                _png_parent = os.path.dirname(out_path)
                if _png_parent:
                    os.makedirs(_png_parent, exist_ok=True)
                fig2 = render_pose_to_figure(row, specs, meshes, v, dpi=dpi)
                save_figure(fig2, out_path)
                print("Wrote", out_path)
        show_figure(fig)
        return data

    # ── 6. GIF or PNG
    views = ["side_view", "front"] if view == "both" else [view]

    png_prefix = _under_dir(output, out_dir)

    if gif:
        multi = view == "both"
        for v in views:
            gif_path = resolve_gif_path(_under_dir(gif, out_dir), v, multi)
            _gif_parent = os.path.dirname(gif_path)
            if _gif_parent:
                os.makedirs(_gif_parent, exist_ok=True)
            render_animation_gif(pose_data, specs, meshes, v, gif_path, fps=fps)
            print("Wrote", gif_path)
    else:
        for v, out_path in resolve_png_outputs(png_prefix, views):
            _png_parent = os.path.dirname(out_path)
            if _png_parent:
                os.makedirs(_png_parent, exist_ok=True)
            fig = render_pose_to_figure(row, specs, meshes, v, dpi=dpi)
            save_figure(fig, out_path)
            print("Wrote", out_path)

    return data


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", nargs="?", default="baseline",
                   choices=["baseline", "custom", "shape"])
    p.add_argument("--height",      type=float, default=None)
    p.add_argument("--weight",      type=float, default=None)
    p.add_argument("--sex",         choices=["male", "female"], default=None)
    p.add_argument("--output-file", default=None,
                   help="Export basename (default: out.xlsx → out.json/.mat/.pkl in run folder)")
    p.add_argument("--param", action="append", default=[], metavar="KEY=VALUE",
                   help="Extra API params, e.g. --param waist_circumference=0.90")

    # Render options (mirrors poser_render CLI)
    p.add_argument("--view",      choices=["side_view", "front", "both"], default="both")
    p.add_argument("--output-dir", default=None, metavar="DIR",
                   help="Run output folder (default: output/<timestamp>_<mode>_<sex>_<weight>_<height>); "
                        "all exports and images go inside")
    p.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Do not prefix --output-dir with a run timestamp (use exact path)",
    )
    p.add_argument("--output",    default="out", metavar="PREFIX",
                   help="PNG filename prefix inside the run output folder (default: out)")
    p.add_argument("--dpi",       type=int, default=150)
    p.add_argument("--gif",       type=str, default=None, metavar="PATH.gif")
    p.add_argument("--fps",       type=int, default=10)
    p.add_argument("--pose-csv",  type=str, default=None, metavar="PATH")
    p.add_argument("--pose-npy",  type=str, default=None, metavar="PATH")
    p.add_argument("--frame",     type=int, default=0)
    p.add_argument(
        "--no-image",
        action="store_true",
        help="Run inertia API + bridge only; skip PNG/GIF generation",
    )
    p.add_argument(
        "--interactive",
        action="store_true",
        help="Open rotatable 3D viewer (drag to orbit, scroll to zoom); skips PNGs unless --save-with-interactive",
    )
    p.add_argument(
        "--save-with-interactive",
        action="store_true",
        help="With --interactive, also write PNGs for --view",
    )

    args = p.parse_args()

    overrides = {}
    if args.height      is not None: overrides["height"]      = args.height
    if args.weight      is not None: overrides["weight"]      = args.weight
    if args.sex         is not None: overrides["sex"]         = args.sex
    if args.output_file is not None:
        overrides["output_file"] = args.output_file
    if args.no_image and not args.interactive:
        overrides["generate_image"] = False
    if args.no_image and args.interactive:
        raise SystemExit("Use either --interactive or --no-image, not both")
    for item in args.param:
        if "=" not in item:
            raise ValueError("Use --param KEY=VALUE")
        k, v = item.split("=", 1)
        try:
            v = float(v)
        except ValueError:
            pass
        overrides[k.strip()] = v

    run(
        mode=args.mode,
        overrides=overrides,
        view=args.view,
        output=args.output,
        gif=args.gif,
        fps=args.fps,
        pose_csv=args.pose_csv,
        pose_npy=args.pose_npy,
        frame=args.frame,
        dpi=args.dpi,
        output_dir=args.output_dir,
        stamp_output_dir=not args.no_timestamp,
        interactive=args.interactive,
        save_with_interactive=args.save_with_interactive,
    )


if __name__ == "__main__":
    main()