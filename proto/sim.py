"""Tiny AABB physics for pad tests — gravity, stacking, piston, motor.

Placed parts are static. Only the crate moves. No tipping: if it is on
top of something, it sits there.
"""

from __future__ import annotations

MAT = {
    "wood": {"mass": 1.2, "bounce": 0.12, "friction": 0.75, "weld": False},
    "steel": {"mass": 2.4, "bounce": 0.06, "friction": 0.55, "weld": False},
    "sticky": {"mass": 1.1, "bounce": 0.0, "friction": 2.8, "weld": True},
    "icy": {"mass": 0.85, "bounce": 0.18, "friction": 0.04, "weld": False},
    "bouncy": {"mass": 0.7, "bounce": 0.82, "friction": 0.25, "weld": False},
    "crate": {"mass": 1.0, "bounce": 0.08, "friction": 0.45, "weld": False},
}

# Everything the player places holds still. The crate is the only body that falls.
STATIC = {"piston", "motor", "brace", "box", "bar", "ball"}


def props(e):
    return MAT.get(getattr(e, "mat", "wood"), MAT["wood"])


def is_dynamic(e):
    return getattr(e, "kind", "box") not in STATIC


def center_y(e):
    return e.y + e.scale_y * 0.5


def top_y(e):
    return e.y + e.scale_y


def set_bottom(e, y):
    e.y = y


def xz_overlap(a, b, pad=0.08):
    dx = (a.scale_x + b.scale_x) * 0.5 - abs(a.x - b.x)
    dz = (a.scale_z + b.scale_z) * 0.5 - abs(a.z - b.z)
    return dx > pad and dz > pad


def overlap(a, b, slop=0.0):
    ax, ay, az = a.x, center_y(a), a.z
    bx, by, bz = b.x, center_y(b), b.z
    dx = (a.scale_x + b.scale_x) * 0.5 - abs(ax - bx) + slop
    dy = (a.scale_y + b.scale_y) * 0.5 - abs(ay - by) + slop
    dz = (a.scale_z + b.scale_z) * 0.5 - abs(az - bz) + slop
    if dx <= 0 or dy <= 0 or dz <= 0:
        return None
    return dx, dy, dz


def land_on(dyn, statics, old_y):
    """Catch a falling crate on the highest top it crossed this step."""
    if dyn.vy > 0.05:
        return False
    best = None
    for s in statics:
        top = top_y(s)
        if old_y + 0.04 < top:
            continue
        if dyn.y > top + 0.02:
            continue
        if not xz_overlap(dyn, s, pad=0.1):
            continue
        if best is None or top > best:
            best = top
    if best is None:
        return False
    set_bottom(dyn, best)
    dyn.vy = 0
    dyn._grounded = True
    return True


def rest_on(dyn, other):
    """Sit on `other` only when already touching its top, not from mid-air."""
    if not xz_overlap(dyn, other, pad=0.1):
        return False
    top = top_y(other)
    if dyn.y > top + 0.1:
        return False
    if center_y(dyn) + 0.04 < center_y(other):
        return False
    set_bottom(dyn, top)
    if dyn.vy < 0:
        dyn.vy = 0
    dyn._grounded = True
    if props(dyn)["weld"] or props(other).get("weld"):
        dyn.vx = 0
        dyn.vz = 0
        dyn.vy = 0
    return True


def separate(dyn, other):
    """Move only `dyn`. Prefer sitting on top over shoving sideways."""
    hit = overlap(dyn, other)
    if not hit:
        return rest_on(dyn, other)
    if rest_on(dyn, other):
        return True
    dx, _dy, dz = hit
    if dx <= dz:
        sign = 1 if dyn.x >= other.x else -1
        dyn.x += sign * dx
        if sign * dyn.vx < 0:
            dyn.vx = 0
    else:
        sign = 1 if dyn.z >= other.z else -1
        dyn.z += sign * dz
        if sign * dyn.vz < 0:
            dyn.vz = 0
    return True
