import numpy as np
from geometry import build_segments
from renderer import draw_model, save_views
from pose_examples import static_pose, simple_animation

# Build body geometry (equivalent to geometric3D_180_140.m)
segments = build_segments()

# ----------------------------
# OPTION 1: Static pose
# ----------------------------
pose = static_pose(segments)

draw_model(segments, pose, view="front")
save_views("geometric_model_front.png")

draw_model(segments, pose, view="side")
save_views("geometric_model_side.png", rotate=90)


# ----------------------------
# OPTION 2: Animation
# ----------------------------
# simple_animation(segments)