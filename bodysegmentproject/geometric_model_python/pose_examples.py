import numpy as np
import matplotlib.pyplot as plt
from renderer import draw_model

def static_pose(segments):
    return None


def simple_animation(segments):

    for t in range(50):

        draw_model(segments, None)

        plt.pause(0.05)
        plt.clf()