"""Tiny AABB physics for pad tests — gravity, stacking, weld islands, break.

Parts fall unless grounded or welded into a grounded island. Actuators
(piston, spring, motor, battery, switch) stay put when on the floor and
act as anchors. Sticky / confirm-weld glues touching parts together.
"""

from __future__ import annotations

MAT = {
    "wood": {"mass": 1.2, "bounce": 0.12, "friction": 0.75, "weld": False, "strength": 1.0},
    "steel": {"mass": 2.4, "bounce": 0.06, "friction": 0.55, "weld": False, "strength": 2.2},
    "sticky": {"mass": 1.1, "bounce": 0.0, "friction": 2.8, "weld": True, "strength": 1.4},
    "icy": {"mass": 0.85, "bounce": 0.18, "friction": 0.04, "weld": False, "strength": 0.8},
    "bouncy": {"mass": 0.7, "bounce": 0.82, "friction": 0.25, "weld": False, "strength": 0.9},
    "sticky_wood": {"mass": 1.3, "bounce": 0.0, "friction": 2.6, "weld": True, "strength": 1.6},
    "sticky_steel": {"mass": 2.5, "bounce": 0.0, "friction": 2.4, "weld": True, "strength": 2.6},
    "crate": {"mass": 1.0, "bounce": 0.08, "friction": 0.45, "weld": False, "strength": 1.0},
}

# Anchors: stay put on the floor and hold welded islands.
ANCHORS = {"piston", "spring", "motor", "battery", "switch"}
# Always dynamic when alone (fall if unsupported).
FALLERS = {"box", "bar", "ball", "plate", "wedge", "brace", "wire"}

# Property mix: placing sticky onto wood/steel cladding.
MIX = {
    ("sticky", "wood"): "sticky_wood",
    ("sticky", "steel"): "sticky_steel",
    ("wood", "sticky"): "sticky_wood",
    ("steel", "sticky"): "sticky_steel",
}


def props(e):
    return MAT.get(getattr(e, "mat", "wood"), MAT["wood"])


def mix_mat(a, b):
    return MIX.get((a, b))


def is_anchor(e):
    return getattr(e, "kind", "") in ANCHORS


def is_dynamic(e):
    """Dynamic unless confirmed into a grounded island or an on-floor anchor."""
    if getattr(e, "kind", "") == "crate":
        return True
    if getattr(e, "_island_static", False):
        return False
    if is_anchor(e) and getattr(e, "_grounded", False):
        return False
    return True


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


def touching(a, b, slop=0.12):
    return overlap(a, b, slop=slop) is not None or (
        xz_overlap(a, b, pad=0.05) and abs(top_y(a) - b.y) < 0.15
    ) or (
        xz_overlap(a, b, pad=0.05) and abs(top_y(b) - a.y) < 0.15
    )


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
    if props(dyn)["weld"] or props(other).get("weld") or getattr(dyn, "welded", False):
        dyn.vx = 0
        dyn.vz = 0
        dyn.vy = 0
    return True


def separate(dyn, other):
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


def _neighbors(parts):
    links = {id(p): [] for p in parts}
    for i, a in enumerate(parts):
        for b in parts[i + 1 :]:
            sticky = props(a)["weld"] or props(b)["weld"]
            forced = getattr(a, "welded", False) and getattr(b, "welded", False)
            if (sticky or forced) and touching(a, b):
                links[id(a)].append(b)
                links[id(b)].append(a)
            elif getattr(a, "welded", False) and touching(a, b):
                # confirmed weld: glue anything touching a welded part
                links[id(a)].append(b)
                links[id(b)].append(a)
    return links


def confirm_welds(parts, floor_y=0.28):
    """Mark touching groups as welded islands. Anchors on the floor pin islands static."""
    for p in parts:
        p.welded = True
        p._island_static = False
        if abs(p.y - floor_y) < 0.08 or p.y <= floor_y + 0.05:
            p._grounded = True
    links = _neighbors(parts)
    seen = set()
    for p in parts:
        if id(p) in seen:
            continue
        stack = [p]
        group = []
        while stack:
            cur = stack.pop()
            if id(cur) in seen:
                continue
            seen.add(id(cur))
            group.append(cur)
            stack.extend(links.get(id(cur), []))
        anchored = any(
            (is_anchor(g) and getattr(g, "_grounded", False)) or g.y <= floor_y + 0.06
            for g in group
        )
        for g in group:
            g._island_static = anchored and len(group) > 0
            g.welded = True


def load_capacity(parts, structure_bias=False):
    """Rough shelf strength from plates/boxes/braces on the pad."""
    total = 0.0
    for p in parts:
        if p.kind in ("box", "plate", "brace", "bar", "wedge"):
            total += props(p)["strength"] * (p.scale_x * p.scale_z) * 0.35
    if structure_bias:
        total *= 1.5
    return total


def break_weak_spans(parts, gap, structure_bias=False):
    """Snap bars/braces that span a gap without enough strength."""
    if not gap:
        return []
    broken = []
    g0, g1 = gap
    mid = (g0 + g1) * 0.5
    need = (g1 - g0) * 0.55
    for p in list(parts):
        if p.kind not in ("bar", "brace", "plate"):
            continue
        # crosses the gap?
        left = p.x - p.scale_x * 0.5
        right = p.x + p.scale_x * 0.5
        if right < g0 or left > g1:
            continue
        if not (left < mid < right or (left <= g0 and right >= g1)):
            # partial overhang into gap
            if not (left < g1 and right > g0 and p.scale_x >= need * 0.6):
                continue
        strength = props(p)["strength"] * p.scale_x
        if structure_bias:
            strength *= 1.5
        if strength < need:
            broken.append(p)
    return broken


def circuit_powered(parts):
    """True when battery touches wire/switch chain that reaches a motor."""
    bats = [p for p in parts if p.kind == "battery"]
    mots = [p for p in parts if p.kind == "motor"]
    sws = [p for p in parts if p.kind == "switch"]
    if not bats or not mots or not sws:
        return False
    # flood from batteries through wire/switch to motor
    conductive = {"battery", "wire", "switch", "motor"}
    nodes = [p for p in parts if p.kind in conductive]
    links = {id(p): [] for p in nodes}
    for i, a in enumerate(nodes):
        for b in nodes[i + 1 :]:
            if touching(a, b, slop=0.2):
                links[id(a)].append(b)
                links[id(b)].append(a)
    for bat in bats:
        seen = set()
        stack = [bat]
        hit_sw = False
        hit_mot = False
        while stack:
            cur = stack.pop()
            if id(cur) in seen:
                continue
            seen.add(id(cur))
            if cur.kind == "switch":
                hit_sw = True
            if cur.kind == "motor":
                hit_mot = True
            stack.extend(links.get(id(cur), []))
        if hit_sw and hit_mot:
            return True
    return False
