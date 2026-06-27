import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from shapes import frustum, ellipsoid
from PIL import Image
import io

def save_views(name, rotate=None):
    buf = io.BytesIO()
    plt.savefig(buf, dpi=300, transparent=True)
    plt.close()

    buf.seek(0)
    img = Image.open(buf)

    if rotate is not None:
        img = img.rotate(rotate, expand=True)

    img.save(name)

def rotate_z(X, Y, Z, angle):
    c = np.cos(angle)
    s = np.sin(angle)

    Xr = c*X - s*Y
    Yr = s*X + c*Y
    return Xr, Yr, Z


def set_axes_equal(ax):
    limits = np.array([
        ax.get_xlim3d(),
        ax.get_ylim3d(),
        ax.get_zlim3d()
    ])
    spans = limits[:,1] - limits[:,0]
    centers = np.mean(limits, axis=1)
    radius = 0.5 * max(spans)

    ax.set_xlim3d([centers[0]-radius, centers[0]+radius])
    ax.set_ylim3d([centers[1]-radius, centers[1]+radius])
    ax.set_zlim3d([centers[2]-radius, centers[2]+radius])


def draw_frustum(ax, P, offset, rot=None):
    xb, yb, zb, xt, yt, zt = frustum(P)

    X = np.vstack([xb, xt])
    Y = np.vstack([yb, yt])
    Z = np.vstack([zb, zt])

    if rot is not None:
        X, Y, Z = rot(X, Y, Z)

    X += offset[0]
    Y += offset[1]
    Z += offset[2]

    ax.plot_surface(X, Y, Z, color="lightgray", linewidth=0)


def draw_ellipsoid(ax, P, offset):
    x, y, z = ellipsoid(P)

    ax.plot_surface(
        x+offset[0],
        y+offset[1],
        z+offset[2],
        color="lightgray",
        linewidth=0
    )


def draw_model(segments, pose=None, view="front"):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    y = 0

    for name in [
        "lower_lowertorso",
        "upper_lowertorso",
        "middle_torso",
        "lower_uppertorso",
        "upper_uppertorso"
    ]:
        P = segments[name]
        draw_frustum(ax, P, [0, y, 0])
        y += P["length"]

    shoulder_y = y

    # head
    draw_ellipsoid(ax, segments["head"], [0, y, 0])

    # -----------------
    # TRUE T-POSE ARMS
    # -----------------
    arm_offset = 0.35

    draw_frustum(
        ax,
        segments["r_arm"],
        [arm_offset, shoulder_y, 0],
        rot=lambda X, Y, Z: rotate_z(X, Y, Z, np.pi/2)
    )

    draw_frustum(
        ax,
        segments["l_arm"],
        [-arm_offset, shoulder_y, 0],
        rot=lambda X, Y, Z: rotate_z(X, Y, Z, -np.pi/2)
    )

    # -----------------
    # HANDS (ROUND)
    # -----------------
    hand_offset = segments["r_arm"]["length"]
    hand_radius = segments["r_hand"]["r"][0]

    draw_ellipsoid(ax, segments["r_hand"], [arm_offset + hand_offset + hand_radius, shoulder_y, 0])
    draw_ellipsoid(ax, segments["l_hand"], [-arm_offset - hand_offset - hand_radius, shoulder_y, 0])

    # -----------------
    # LEGS
    # -----------------
    leg_offset = 0.12

    draw_frustum(
        ax,
        segments["r_leg"],
        [leg_offset, -segments["r_leg"]["length"], 0]
    )

    draw_frustum(
        ax,
        segments["l_leg"],
        [-leg_offset, -segments["l_leg"]["length"], 0]
    )

    set_axes_equal(ax)
    ax.axis("off")

    if view == "front":
        ax.view_init(elev=90, azim=-90)

    if view == "side":
        ax.view_init(elev=0, azim=0)

    plt.tight_layout()
