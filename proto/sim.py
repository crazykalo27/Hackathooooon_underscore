"""Tiny AABB physics for pad tests — gravity, collisions, piston, motor."""

from __future__ import annotations

MAT = {
    "wood": {"mass": 1.2, "bounce": 0.12, "friction": 0.75, "weld": False},
    "steel": {"mass": 2.4, "bounce": 0.06, "friction": 0.55, "weld": False},
    "sticky": {"mass": 1.1, "bounce": 0.0, "friction": 2.8, "weld": True},
    "icy": {"mass": 0.85, "bounce": 0.18, "friction": 0.04, "weld": False},
    "bouncy": {"mass": 0.7, "bounce": 0.82, "friction": 0.25, "weld": False},
    "crate": {"mass": 1.0, "bounce": 0.1, "friction": 0.6, "weld": False},
}

KINEMATIC = {"piston", "motor", "brace"}


def props(e):
    return MAT.get(getattr(e, "mat", "wood"), MAT["wood"])


def is_dynamic(e):
    return getattr(e, "kind", "box") not in KINEMATIC


def center_y(e):
    # parts use origin_y = -0.5, so position is the bottom
    return e.y + e.scale_y * 0.5


def top_y(e):
    return e.y + e.scale_y


def set_bottom(e, y):
    e.y = y


def overlap(a, b, slop=0.0):
    ax, ay, az = a.x, center_y(a), a.z
    bx, by, bz = b.x, center_y(b), b.z
    dx = (a.scale_x + b.scale_x) * 0.5 - abs(ax - bx) + slop
    dy = (a.scale_y + b.scale_y) * 0.5 - abs(ay - by) + slop
    dz = (a.scale_z + b.scale_z) * 0.5 - abs(az - bz) + slop
    if dx <= 0 or dy <= 0 or dz <= 0:
        return None
    return dx, dy, dz


def separate(dyn, other):
    hit = overlap(dyn, other)
    if not hit:
        return False
    dx, dy, dz = hit
    axis = min((dx, "x"), (dy, "y"), (dz, "z"))
    pen, name = axis
    sign = 1
    if name == "x":
        sign = 1 if dyn.x >= other.x else -1
        dyn.x += sign * pen
        if sign * dyn.vx < 0:
            dyn.vx *= -props(dyn)["bounce"]
        dyn.vx *= 1 - min(1, props(dyn)["friction"] * 0.15)
    elif name == "z":
        sign = 1 if dyn.z >= other.z else -1
        dyn.z += sign * pen
        if sign * dyn.vz < 0:
            dyn.vz *= -props(dyn)["bounce"]
        dyn.vz *= 1 - min(1, props(dyn)["friction"] * 0.15)
    else:
        sign = 1 if center_y(dyn) >= center_y(other) else -1
        if sign > 0:
            set_bottom(dyn, top_y(other))
        else:
            set_bottom(dyn, other.y - dyn.scale_y)
        if sign * dyn.vy < 0:
            dyn.vy *= -props(dyn)["bounce"]
        if abs(dyn.vy) < 0.4:
            dyn.vy = 0
        mu = props(dyn)["friction"]
        dyn.vx *= max(0, 1 - mu * 0.08)
        dyn.vz *= max(0, 1 - mu * 0.08)
        if props(dyn)["weld"] or props(other).get("weld"):
            dyn.vx = 0
            dyn.vz = 0
            dyn.vy = 0
            dyn._grounded = True
        else:
            dyn._grounded = True
    return True
