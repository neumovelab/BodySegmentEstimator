import numpy as np

def frustum(P):

    theta = np.linspace(0,2*np.pi,P["res"])

    xb = P["r_bottom"][0]*np.cos(theta)
    zb = P["r_bottom"][1]*np.sin(theta)
    yb = np.zeros_like(theta)

    xt = P["r_top"][0]*np.cos(theta)
    zt = P["r_top"][1]*np.sin(theta)
    yt = np.ones_like(theta)*P["length"]

    return xb, yb, zb, xt, yt, zt


def ellipsoid(P):

    theta = np.linspace(0,2*np.pi,P["res"])
    phi = np.linspace(0,np.pi,P["res"])

    TH,PH = np.meshgrid(theta,phi)

    x = P["r"][0]*np.sin(PH)*np.cos(TH)
    z = P["r"][1]*np.sin(PH)*np.sin(TH)
    y = (P["length"]/2)*np.cos(PH)+(P["length"]/2)

    return x,y,z

def cone(P):
    theta = np.linspace(0, 2*np.pi, P["res"])

    xb = P["r"][0] * np.cos(theta)
    zb = P["r"][1] * np.sin(theta)
    yb = np.zeros_like(theta)

    xt = np.zeros_like(theta)
    zt = np.zeros_like(theta)
    yt = np.ones_like(theta) * P["length"]

    return xb, yb, zb, xt, yt, zt