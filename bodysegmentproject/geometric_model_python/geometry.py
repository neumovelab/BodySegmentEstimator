import numpy as np

def build_segments():

    res = 60
    segments = {}

    # -------------------
    # HEAD
    # -------------------
    segments["head"] = dict(
        shape="ellipsoid",
        length=0.24,
        r=[0.095, 0.095],
        res=res
    )

    # -------------------
    # ORIGINAL TORSO LENGTHS
    # -------------------
    upper_torso_len  = 0.15
    middle_torso_len = 0.24
    lower_torso_len  = 0.16

    # -------------------
    # SPLIT INTO 5 SEGMENTS
    # -------------------
    upper_uppertorso = 0.4 * upper_torso_len
    lower_uppertorso = 0.6 * upper_torso_len

    middle_torso = middle_torso_len

    upper_lowertorso = 0.5 * lower_torso_len
    lower_lowertorso = 0.5 * lower_torso_len

    # -------------------
    # 5 SEGMENT TORSO
    # -------------------

    segments["lower_lowertorso"] = dict(
        shape="cone",
        length=lower_lowertorso,
        r=[0.20,0.22],
        r_bottom=[0.35,0.40],
        res=res
    )

    segments["upper_lowertorso"] = dict(
        shape="frustum",
        length=upper_lowertorso,
        r_bottom=[0.30,0.35],
        r_top=[0.22,0.25],
        off_top=[0,0],
        res=res
    )

    segments["middle_torso"] = dict(
        shape="frustum",
        length=middle_torso,
        r_bottom=[0.22,0.25],
        r_top=[0.18,0.20],
        off_top=[0,0],
        res=res
    )

    segments["lower_uppertorso"] = dict(
        shape="frustum",
        length=lower_uppertorso,
        r_bottom=[0.18,0.20],
        r_top=[0.14,0.16],
        off_top=[0,0],
        res=res
    )

    segments["upper_uppertorso"] = dict(
        shape="frustum",
        length=upper_uppertorso,
        r_bottom=[0.14,0.16],
        r_top=[0.072,0.072],
        off_top=[0,0],
        res=res
    )

    # -------------------
    # ARMS
    # -------------------
    
    segments["r_hand"] = dict(
        shape="ellipsoid",
        length=0.10,
        r=[0.05, 0.05],
        res=res
    )

    segments["l_hand"] = dict(
        shape="ellipsoid",
        length=0.10,
        r=[0.05, 0.05],
        res=res
    )

    segments["r_arm"] = dict(
        shape="frustum",
        length=0.34,
        r_bottom=[0.07,0.07],
        r_top=[0.05,0.05],
        off_top=[0,0],
        res=res
    )

    segments["l_arm"] = dict(
        shape="frustum",
        length=0.34,
        r_bottom=[0.07,0.07],
        r_top=[0.05,0.05],
        off_top=[0,0],
        res=res
    )

    # -------------------
    # LEGS
    # -------------------
    segments["r_leg"] = dict(
        shape="frustum",
        length=0.5,
        r_bottom=[0.08,0.08],
        r_top=[0.04,0.04],
        off_top=[0,0],
        res=res
    )

    segments["l_leg"] = dict(
        shape="frustum",
        length=0.5,
        r_bottom=[0.08,0.08],
        r_top=[0.04,0.04],
        off_top=[0,0],
        res=res
    )

    return segments