"""Readable 3D maps as stacked pastel solids."""

from __future__ import annotations

import math

from ursina import Entity, Vec3, destroy, scene

from proto import story
from proto.config import (
    ACCENT,
    BRASS,
    BRASS_D,
    COPPER,
    CREAM,
    EARTH_CLIFF,
    EARTH_DIRT,
    EARTH_SAND,
    GOLD,
    IRON,
    IRON_B,
    LAMP,
    PATINA,
    SHADOW,
    SHIP_FLOOR,
    SHIP_ROSE,
    SHIP_WALL,
    SKY,
    SPACE,
    STAR,
    STAR_DIM,
    TEAL,
    HULL_CEIL,
)
from proto.figure import attach, shade
from proto.visuals import mood, solid

STEEL_TOTEM = (176, 188, 204)


def _cut_radius(dist):
    return 8.0 + max(dist, 4.0) * 0.34


def cut_screen_radius(dist, fov=None, aspect=None):
    """Same NDC ring the hull shader uses (vertical NDC units)."""
    from ursina import camera

    from proto.config import CAM_FOV

    fov = fov if fov is not None else getattr(camera, "fov", CAM_FOV)
    half = math.tan(math.radians(max(float(fov), 1.0)) * 0.5)
    ndc = _cut_radius(dist) / max(dist, 1.0) / max(half, 0.05)
    return max(0.32, min(0.86, ndc))


class World:
    def __init__(self):
        self.root = None
        self.npcs = []
        self.pads = {}
        self.hull = []
        self._cut = None
        self.map_name = "ship"

    def clear(self):
        if self.root:
            destroy(self.root)
        self.root = Entity()
        self.npcs.clear()
        self.pads.clear()
        self.hull.clear()
        self._cut = None

    def load(self, map_name: str, flags: dict):
        from ursina import color, window

        self.clear()
        self.map_name = map_name
        scene.fog_density = 0
        window.color = color.rgb(*(SPACE if map_name == "ship" else SKY))
        mood(map_name)
        if map_name == "ship":
            self._ship(flags)
        elif map_name == "c2":
            self._c2(flags)
        else:
            self._earth(flags)

    def _box(self, col, pos, scale, collider=None, face=None, model="cube", rot=None):
        e = solid(col, hull=bool(face), parent=self.root, model=model, position=pos, scale=scale, collider=collider)
        if rot:
            e.rotation = rot
        if face:
            e.hull_face = face
            self.hull.append(e)
        return e

    def _orb(self, col, pos, scale, face=None, rot=None):
        if isinstance(scale, (int, float)):
            scale = (scale, scale, scale)
        return self._box(col, pos, scale, model="sphere", face=face, rot=rot)

    def set_hull_hidden(self, hide):
        if not hide:
            self.apply_cutaway(None, None, 0)
            return
        self.apply_cutaway(hide.get("cam"), hide.get("look"), hide.get("dist", 26))

    def apply_cutaway(self, cam, look, dist=26):
        if cam is None or look is None or self.map_name != "ship":
            self._cut = None
            for e in self.hull:
                e.visible = True
                e.set_shader_input("cut_ndc", 0.0)
            return
        from ursina import camera

        ndc = cut_screen_radius(dist)
        aspect = float(getattr(camera, "aspect_ratio", 1.6) or 1.6)
        key = (int(ndc * 80), int(aspect * 20), int(look.x * 4), int(look.z * 4))
        if key == self._cut:
            return
        self._cut = key
        for e in self.hull:
            e.visible = True
            e.set_shader_input("cut_ndc", ndc)
            e.set_shader_input("cut_aspect", aspect)

    def _span_x(self, col, y, z, x0, x1, h, d, face=None, collider=None, bay=8.0):
        x = x0
        while x < x1 - 0.02:
            w = min(bay, x1 - x)
            self._box(col, (x + w * 0.5, y, z), (w, h, d), collider=collider, face=face)
            x += bay

    def _arch(self, x, col=IRON):
        from proto.config import HALL_HALF

        z = HALL_HALF - 0.4
        self._box(col, (x, 3.6, -z), (0.7, 7.2, 0.55), face="s")
        self._box(col, (x, 3.6, z), (0.7, 7.2, 0.55), face="n")
        self._box(col, (x, 7.35, 0), (0.7, 0.5, HALL_HALF * 2), face="ceil")
        self._box(BRASS, (x, 7.12, 0), (0.9, 0.12, HALL_HALF * 2 - 0.5), face="ceil")
        self._box(BRASS, (x, 0.1, 0), (0.55, 0.14, HALL_HALF * 2 - 1.4))

    def _starfield(self, length, start=0, count=140):
        import random

        from proto.config import HALL_HALF

        hz = HALL_HALF
        rng = random.Random(21)
        for i in range(start + count):
            side = rng.choice(("n", "s", "up", "w", "e"))
            if side == "n":
                pos = (rng.uniform(-20, length + 20), rng.uniform(-8, 28), rng.uniform(hz + 48, hz + 110))
            elif side == "s":
                pos = (rng.uniform(-20, length + 20), rng.uniform(-8, 28), rng.uniform(-(hz + 110), -(hz + 48)))
            elif side == "up":
                pos = (rng.uniform(-30, length + 30), rng.uniform(22, 58), rng.uniform(-(hz + 40), hz + 40))
            elif side == "w":
                pos = (rng.uniform(-90, -32), rng.uniform(-6, 24), rng.uniform(-(hz + 40), hz + 40))
            else:
                pos = (rng.uniform(length + 24, length + 90), rng.uniform(-6, 24), rng.uniform(-(hz + 40), hz + 40))
            s = rng.choice((0.07, 0.09, 0.12, 0.16, 0.22, 0.34))
            col = STAR if rng.random() > 0.28 else STAR_DIM
            if i < start:
                continue
            self._box(col, pos, (s, s, s))

    def _star_props(self, length):
        self._deep_space()
        self._ext_earth()

    def _window(self, x, z, w=3.1, h=2.15, y=2.18, face=None):
        inward = -0.12 if z > 0 else 0.12
        fz = z + inward
        self._box(BRASS, (x - w * 0.5, y, fz), (0.16, h, 0.22), face=face)
        self._box(BRASS, (x + w * 0.5, y, fz), (0.16, h, 0.22), face=face)
        self._box(BRASS, (x, y + h * 0.5, fz), (w + 0.16, 0.16, 0.22), face=face)
        self._box(BRASS, (x, y - h * 0.5, fz), (w + 0.16, 0.16, 0.22), face=face)
        self._box(BRASS_D, (x, y, fz), (0.1, h, 0.12), face=face)
        for rx in (-w * 0.42, 0, w * 0.42):
            self._box(BRASS, (x + rx, y - h * 0.5, fz), (0.14, 0.14, 0.26), face=face)
            self._box(BRASS, (x + rx, y + h * 0.5, fz), (0.14, 0.14, 0.26), face=face)

    def _hull_side(self, length, z, col, face):
        self._span_x(col, 0.5, z, -4.0, length + 4.0, 1.0, 0.5, face=face, collider="box")
        self._span_x(BRASS, 1.02, z + (-0.02 if z > 0 else 0.02), -4.0, length + 4.0, 0.08, 0.56, face=face)
        self._span_x(col, 3.95, z, -4.0, length + 4.0, 1.12, 0.5, face=face, collider="box")
        self._span_x(col, 6.3, z, -4.0, length + 4.0, 3.6, 0.5, face=face, collider="box")
        spacing = 9.0
        win_w = 3.1
        windows = [4.0 + i * spacing for i in range(int((length - 6) / spacing))]
        prev = -4.0
        for wx in windows:
            left = wx - win_w * 0.5
            pier_w = left - prev
            if pier_w > 0.35:
                self._box(col, ((prev + left) * 0.5, 2.15, z), (pier_w, 2.3, 0.5), collider="box", face=face)
            self._window(wx, z, win_w, face=face)
            prev = wx + win_w * 0.5
        end = length + 4.0
        pier_w = end - prev
        if pier_w > 0.35:
            self._box(col, ((prev + end) * 0.5, 2.15, z), (pier_w, 2.3, 0.5), collider="box", face=face)
        self._dress_wall(length, z, face, windows)

    def _dress_wall(self, length, z, face, windows):
        inward = -0.28 if z > 0 else 0.28
        fz = z + inward
        self._span_x(BRASS, 4.55, fz, 3.0, length - 3.0, 0.16, 0.16, face=face)
        self._span_x(COPPER, 4.78, fz, 4.0, length - 4.0, 0.1, 0.1, face=face)
        for x in range(2, int(length), 2):
            self._box(BRASS, (x, 1.04, fz), (0.12, 0.12, 0.12), face=face)
        for i, wx in enumerate(windows):
            if i % 2:
                continue
            gx = wx - 2.2
            self._box(IRON, (gx, 3.15, fz), (0.32, 0.32, 0.12), face=face)
            self._box(BRASS, (gx, 3.15, fz + inward * 0.15), (0.4, 0.4, 0.08), face=face)
            self._box(LAMP, (gx, 3.15, fz + inward * 0.28), (0.08, 0.08, 0.1), face=face)
        for x in range(10, int(length), 18):
            self._box(BRASS, (x, 2.6, fz), (0.22, 2.4, 0.22), face=face)
            self._box(BRASS_D, (x, 1.35, fz), (0.5, 0.12, 0.5), face=face)
            self._box(BRASS, (x, 1.35, fz), (0.12, 0.12, 0.55), face=face)

    def _deck(self, length, hz, wide):
        self._box(SHIP_FLOOR, (length / 2, -0.22, 0), (length + 10, 0.44, wide), collider="box")
        tw, td = 4.0, 4.2
        zi = -hz + 1.8
        row = 0
        while zi < hz - 1.4:
            xi = -2.0
            col = 0
            while xi < length:
                plate = IRON if (row + col) % 2 == 0 else IRON_B
                self._box(plate, (xi + tw * 0.5, 0.04, zi + td * 0.5), (tw - 0.14, 0.08, td - 0.14))
                if (row + col) % 2 == 0:
                    self._box(BRASS_D, (xi + 0.2, 0.1, zi + 0.2), (0.14, 0.08, 0.14))
                    self._box(BRASS_D, (xi + tw - 0.2, 0.1, zi + td - 0.2), (0.14, 0.08, 0.14))
                xi += tw
                col += 1
            zi += td
            row += 1
        self._box(BRASS, (length / 2, 0.09, 0), (length + 4, 0.06, 0.55))
        for x in range(4, int(length), 8):
            self._box(BRASS_D, (x, 0.12, 0), (0.35, 0.1, hz * 2 - 2.2))

    def _ceiling(self, length, hz, wide):
        for x in range(2, int(length), 8):
            self._box(IRON, (x + 2.2, HULL_CEIL, 0), (5.2, 0.24, wide - 0.5), face="ceil")
            self._box(BRASS, (x + 5.5, HULL_CEIL, 0), (0.32, 0.18, wide - 0.8), face="ceil")
        self._span_x(COPPER, HULL_CEIL - 0.35, 4.2, 4.0, length - 4.0, 0.14, 0.14, face="ceil")
        self._span_x(COPPER, HULL_CEIL - 0.35, -4.2, 4.0, length - 4.0, 0.14, 0.14, face="ceil")
        for x in range(8, int(length), 12):
            self._box(IRON, (x, HULL_CEIL - 0.55, 0), (0.12, 0.7, 0.12), face="ceil")
            self._box(LAMP, (x, HULL_CEIL - 0.95, 0), (0.5, 0.22, 0.5), face="ceil")
            self._box(BRASS, (x, HULL_CEIL - 0.82, 0), (0.62, 0.08, 0.62), face="ceil")

    def _west_viewport(self, hz):
        wide = hz * 2 + 0.8
        gap = 2.15
        wing_d = hz + 0.4 - gap
        wing_c = gap + wing_d * 0.5
        self._box(IRON, (-4.5, 0.5, 0), (0.5, 1.0, wide), collider="box", face="w")
        self._box(IRON, (-4.5, 6.1, 0), (0.5, 4.0, wide), collider="box", face="w")
        self._box(IRON, (-4.5, 2.55, -wing_c), (0.5, 3.1, wing_d), collider="box", face="w")
        self._box(IRON, (-4.5, 2.55, wing_c), (0.5, 3.1, wing_d), collider="box", face="w")
        self._box(BRASS, (-4.35, 2.2, -gap), (0.2, 2.4, 0.16), face="w")
        self._box(BRASS, (-4.35, 2.2, gap), (0.2, 2.4, 0.16), face="w")
        self._box(BRASS, (-4.35, 3.4, 0), (0.2, 0.16, gap * 2), face="w")
        self._box(BRASS, (-4.35, 1.05, 0), (0.2, 0.16, gap * 2), face="w")
        self._box(LAMP, (-4.5, HULL_CEIL, 0), (0.55, 0.22, 2.4), face="w")
        self._box(COPPER, (-4.2, 0.35, 0), (0.4, 0.4, 1.2), face="w")

    def _east_bulkhead(self, length, hz):
        wide = hz * 2 + 0.8
        x = length + 4.2
        self._box(IRON, (x, 0.5, 0), (0.5, 1.0, wide), collider="box", face="e")
        self._box(IRON, (x, 3.95, 0), (0.5, 5.9, wide), collider="box", face="e")
        self._box(BRASS, (x - 0.18, 2.3, 0), (0.22, 2.6, 2.6), face="e")
        self._box(COPPER, (x - 1.1, 1.4, 4.5), (1.6, 2.6, 1.6))
        self._box(BRASS, (x - 1.1, 2.8, 4.5), (1.75, 0.18, 1.75))
        self._box(IRON, (x - 1.1, 1.5, -4.5), (1.4, 2.8, 1.4))
        self._box(BRASS, (x - 1.1, 3.0, -4.5), (1.55, 0.16, 1.55))
        self._box(PATINA, (x - 1.1, 3.4, -4.5), (0.5, 0.4, 0.5))

    def _label(self, x, text, y=2.4, z=-4.35):
        w = min(0.28 * max(len(text), 4), 2.6)
        return self._box(GOLD, (x, y, z), (w, 0.12, 0.12))

    def _person(self, defn):
        root = Entity(parent=self.root, position=(defn.x, 0, defn.z), rotation_y=defn.rot)
        Entity(
            parent=root,
            model="cube",
            position=(0, 0.85, 0),
            scale=(0.5, 1.7, 0.4),
            collider="box",
            visible=False,
        )
        hair = shade(defn.color, 0.45)
        attach(root, shirt=defn.color, pants=shade(defn.color, 0.68), hair=hair, accent=defn.color)
        root.npc_id = defn.id
        root.npc_name = defn.name
        root.talk_id = defn.talk
        self.npcs.append(root)
        return root

    def _pad(self, zone):
        if zone.gap:
            left, right = zone.gap
            lw = max(1.2, left - (zone.x - zone.w * 0.5))
            rw = max(1.2, (zone.x + zone.w * 0.5) - right)
            self._box(SHADOW, ((zone.x - zone.w * 0.5) + lw * 0.5, 0.02, zone.z), (lw + 0.3, 0.04, zone.d + 0.3))
            self._box(zone.color, ((zone.x - zone.w * 0.5) + lw * 0.5, 0.12, zone.z), (lw, 0.22, zone.d))
            self._box(SHADOW, ((zone.x + zone.w * 0.5) - rw * 0.5, 0.02, zone.z), (rw + 0.3, 0.04, zone.d + 0.3))
            pad = self._box(zone.color, ((zone.x + zone.w * 0.5) - rw * 0.5, 0.12, zone.z), (rw, 0.22, zone.d))
            self._box((90, 70, 62), ((left + right) * 0.5, -1.2, zone.z), (right - left, 2.2, zone.d * 0.85))
        else:
            self._box(SHADOW, (zone.x, 0.02, zone.z), (zone.w + 0.4, 0.04, zone.d + 0.4))
            pad = self._box(zone.color, (zone.x, 0.12, zone.z), (zone.w, 0.22, zone.d))
            top = tuple(min(255, c + 28) for c in zone.color[:3])
            self._box(top, (zone.x, 0.26, zone.z), (zone.w * 0.84, 0.06, zone.d * 0.84))
        pad.zone = zone
        self.pads[zone.key] = pad
        return pad

    def _deep_space(self):
        import random

        rng = random.Random(77)
        for _ in range(110):
            pos = (
                rng.uniform(-260, 320),
                rng.uniform(-120, 160),
                rng.uniform(-280, 280),
            )
            if abs(pos[0] - 46) < 90 and abs(pos[1] - 2) < 50 and abs(pos[2]) < 70:
                continue
            s = rng.choice((0.4, 0.55, 0.8, 1.2, 1.8, 2.6))
            self._orb(STAR if rng.random() > 0.35 else STAR_DIM, pos, s)
        self._orb(LAMP, (240, 110, 280), 16)
        self._orb(GOLD, (246, 112, 286), 7)

    def _ext_earth(self):
        # Far below/south — continents sit on the ship-facing hemisphere.
        c = (52, -186, -96)
        self._orb((34, 86, 162), c, 248)
        self._orb((58, 124, 72), (c[0] + 18, c[1] + 78, c[2] + 22), 92)
        self._orb((138, 118, 64), (c[0] - 28, c[1] + 70, c[2] - 36), 74)
        self._orb((168, 142, 78), (c[0] + 40, c[1] + 62, c[2] - 20), 48)
        self._orb((46, 98, 64), (c[0] + 52, c[1] + 48, c[2] + 40), 58)
        self._orb((228, 236, 246), (c[0] - 4, c[1] + 108, c[2] - 6), 44)
        self._orb((164, 168, 174), (178, -128, -236), 20)
        self._orb((118, 124, 132), (186, -124, -242), 8)

    def _ext_nose(self, hz):
        self._orb(IRON, (-12, 6.5, 0), (15, 3.0, 16), face=("w", "ceil"))
        self._orb(IRON_B, (-12, -0.7, 0), (15, 2.2, 15))
        self._orb(IRON, (-10.5, 3.3, 9.6), (12, 5.8, 8.2), face=("n", "w"))
        self._orb(IRON, (-10.5, 3.3, -9.6), (12, 5.8, 8.2), face=("s", "w"))
        self._orb(IRON_B, (-19, 1.05, 0), (11, 1.9, 3.2), face="w")
        self._orb(IRON, (-25.5, 0.95, 0), (8, 1.35, 1.9), face="w")
        self._orb(BRASS, (-29.4, 0.95, 0), (3.2, 0.9, 0.9), face="w")
        self._orb(LAMP, (-31.2, 0.95, 0), 1.05, face="w")
        self._orb(GOLD, (-32.0, 0.95, 0), 0.5, face="w")
        self._box(BRASS_D, (-8.8, 7.2, 0), (9, 0.18, 12), rot=(0, 0, 11), face=("w", "ceil"))
        self._box(COPPER, (-9.2, 5.5, 6.6), (0.18, 0.18, 9), rot=(0, 20, 9), face="n")
        self._box(COPPER, (-9.2, 5.5, -6.6), (0.18, 0.18, 9), rot=(0, -20, -9), face="s")
        for s in (-1, 1):
            face = "n" if s > 0 else "s"
            self._box(IRON, (-15, 0.85, s * (hz + 4.2)), (12, 0.22, 5.5), rot=(s * 8, s * 16, s * 5), face=face)
            self._box(BRASS_D, (-12, 0.95, s * (hz + 6.5)), (7, 0.12, 3.2), rot=(s * 8, s * 18, 0), face=face)

    def _ext_keel(self, length, hz):
        self._orb(IRON, (18, -2.8, 0), (32, 3.2, 18))
        self._orb(IRON_B, (48, -3.05, 0), (38, 3.5, 19))
        self._orb(IRON, (76, -2.7, 0), (30, 3.0, 16))
        self._box(BRASS_D, (length / 2, -3.6, 0), (length + 10, 0.28, 0.85))
        self._box(COPPER, (length / 2, -3.1, 0), (length - 6, 0.12, 0.28))
        for x in (16, 40, 64, 84):
            self._orb(BRASS, (x, -3.85, 0), (2.1, 1.0, 2.1))
        for s in (-1, 1):
            face = "n" if s > 0 else "s"
            x = 8.0
            while x < length - 4:
                self._orb(IRON, (x + 5, 6.6, s * (hz + 3.6)), (12, 3.0, 6.4), face=face)
                self._orb(IRON_B, (x + 5, -0.05, s * (hz + 3.4)), (12, 1.7, 6.0), face=face)
                x += 10.0
            self._span_x(BRASS_D, 5.15, s * (hz + 0.55), 10.0, length - 10.0, 0.14, 0.2, face=face)
        self._span_x(IRON, HULL_CEIL + 0.58, 0, -2.0, length + 6.0, 0.8, hz * 2 + 0.8, face="ceil", bay=10.0)
        x = 4.0
        while x < length:
            self._orb(IRON, (x + 5, 10.6, 0), (14, 4.2, 28), face="ceil")
            x += 10.0
        self._orb(IRON, (60, 12.4, 0), (26, 4.8, 1.6), face="ceil")
        self._box(IRON_B, (66, 13.2, 0), (20, 5.0, 0.4), rot=(0, 0, -11), face="ceil")
        self._box(BRASS, (78, 16.2, 0), (0.22, 5.2, 0.22), face="ceil")
        self._orb(LAMP, (78, 19.0, 0), 0.9)
        self._box(COPPER, (42, 11.3, 7.5), (18, 0.1, 7), rot=(62, 0, 0), face="ceil")
        self._box(COPPER, (42, 11.3, -7.5), (18, 0.1, 7), rot=(-62, 0, 0), face="ceil")

    def _ext_wings(self, length, hz):
        for side in (-1, 1):
            s = float(side)
            z0 = s * hz
            face = "n" if s > 0 else "s"
            self._orb(IRON, (48, 0.62, z0 + s * 11), (30, 0.62, 20), face=face)
            self._orb(IRON_B, (64, 0.72, z0 + s * 22), (26, 0.48, 18), face=face)
            self._orb(IRON, (78, 0.82, z0 + s * 32), (18, 0.36, 12), face=face)
            self._box(IRON, (58, 0.68, z0 + s * 16), (36, 0.22, 14), rot=(s * 4, s * 24, s * 4), face=face)
            self._box(BRASS_D, (70, 0.78, z0 + s * 26), (16, 0.1, 7), rot=(s * 3, s * 28, s * 3), face=face)
            self._box(COPPER, (52, 0.9, z0 + s * 8), (22, 0.08, 3.5), rot=(0, s * 18, 0), face=face)
            self._box(BRASS, (40, 0.95, z0 + s * 3.2), (0.22, 0.22, 8), face=face)
            self._box(BRASS, (62, 0.95, z0 + s * 14), (0.2, 0.2, 12), face=face)
            self._orb(IRON, (88, 0.95, z0 + s * 36), (3.4, 2.2, 2.6), face=face)
            self._orb(BRASS, (89.2, 0.95, z0 + s * 36), 1.15, face=face)
            self._orb(LAMP, (90.4, 0.95, z0 + s * 36), 0.85, face=face)
            self._orb(GOLD, (91.0, 0.95, z0 + s * 36), 0.45, face=face)
            for x in (22, 36, 52, 68):
                self._orb(LAMP, (x, 0.38, z0 + s * 0.7), 0.22, face=face)

    def _ext_engines(self, length, hz):
        aft = length + 11
        for z, y, size in ((0.0, 2.5, 1.05), (7.4, 1.5, 0.82), (-7.4, 1.5, 0.82), (0.0, 5.8, 0.72)):
            k = size
            self._orb(IRON, (aft - 3, y, z), (7.0 * k, 3.8 * k, 3.8 * k), face="e")
            self._orb(IRON_B, (aft + 2.2, y, z), (3.8 * k, 4.4 * k, 4.4 * k), face="e")
            self._box(BRASS, (aft + 1.0, y, z), (0.34, 4.6 * k, 4.6 * k), face="e")
            self._box(COPPER, (aft + 2.6, y, z), (0.24, 3.7 * k, 3.7 * k), face="e")
            self._orb(LAMP, (aft + 5.4, y, z), (2.6 * k, 3.4 * k, 3.4 * k), face="e")
            self._orb(GOLD, (aft + 7.0, y, z), (1.8 * k, 2.4 * k, 2.4 * k), face="e")
            self._orb(ACCENT, (aft + 8.2, y, z), (1.0 * k, 1.4 * k, 1.4 * k), face="e")
        self._orb(IRON, (length + 6, 3.4, 0), (10, 6.4, 10), face="e")
        self._box(BRASS_D, (length + 4.6, 7.2, 0), (8.5, 0.2, 8.5), face="e")
        for ang in range(0, 360, 45):
            r = 3.8
            rz = math.sin(math.radians(ang)) * r
            ry = 3.4 + math.cos(math.radians(ang)) * r
            self._orb(BRASS, (length + 8.8, ry, rz), 0.5, face="e")

    def _ext_skin(self, length, hz):
        self._ext_nose(hz)
        self._ext_keel(length, hz)
        self._ext_wings(length, hz)
        self._ext_engines(length, hz)

    def _ship(self, flags):
        from proto.config import HALL_HALF, SHIP_LEN

        length = SHIP_LEN
        hz = HALL_HALF
        wide = hz * 2 + 0.8
        self._starfield(length)
        self._star_props(length)
        self._deck(length, hz, wide)
        self._hull_side(length, -hz - 0.22, SHIP_ROSE, "s")
        self._hull_side(length, hz + 0.22, SHIP_WALL, "n")
        self._west_viewport(hz)
        self._east_bulkhead(length, hz)
        self._ceiling(length, hz, wide)
        self._ext_skin(length, hz)
        for x in range(8, int(length), 12):
            self._arch(x, IRON if (x // 12) % 2 == 0 else IRON_B)
        self._ship_props(length, hz)
        for z in story.SHIP_ZONES:
            self._pad(z)
        self._ship_people(flags)

    def _ship_props(self, length, hz):
        self._box(IRON, (3.2, 0.28, -2.2), (3.3, 0.4, 2.1), collider="box")
        self._box(BRASS, (1.7, 0.7, -2.9), (0.22, 1.1, 0.22))
        self._box(BRASS, (4.7, 0.7, -1.5), (0.22, 1.1, 0.22))
        self._box(COPPER, (3.2, 0.62, -2.2), (2.8, 0.22, 1.6))
        self._box(LAMP, (4.5, 1.15, -2.2), (0.28, 0.22, 0.28))
        self._box(IRON, (10.5, 1.7, -hz + 0.4), (2.3, 1.6, 0.18), face="s")
        self._box(BRASS, (10.5, 1.7, -hz + 0.52), (1.5, 1.0, 0.1), face="s")
        self._box(IRON, (14, 0.35, -hz + 1.6), (2.5, 0.7, 1.1), collider="box")
        self._box(BRASS, (14, 0.78, -hz + 1.6), (2.6, 0.1, 1.2))
        self._box(PATINA, (14.9, 0.55, -hz + 1.1), (0.35, 0.45, 0.35))
        ex = length - 3.5
        self._box(IRON, (ex, 1.15, 0), (2.3, 2.3, 2.3), collider="box")
        self._box(BRASS, (ex, 0.45, 0), (2.5, 0.2, 2.5))
        self._box(BRASS, (ex, 2.4, 0), (2.5, 0.18, 2.5))
        self._box(COPPER, (ex, 3.2, 0), (1.1, 1.4, 1.1))
        self._box(LAMP, (ex, 4.0, 0), (0.45, 0.25, 0.45))

    def _ship_people(self, flags):
        for n in story.SHIP_NPCS:
            if n.show_if and not flags.get(n.show_if):
                continue
            if n.hide_if and flags.get(n.hide_if):
                continue
            self._person(n)

    def begin_boot_load(self, flags):
        from ursina import color, window

        from proto.config import HALL_HALF, SHIP_LEN

        self.clear()
        self.map_name = "ship"
        scene.fog_density = 0
        window.color = color.rgb(*SPACE)
        mood("ship")
        length = SHIP_LEN
        hz = HALL_HALF
        wide = hz * 2 + 0.8
        self._boot_i = 0
        self.load_status = "STARS"
        self.load_frac = 0.0
        star_steps = [
            (f"STARS {n + 1}", lambda start=start: self._starfield(length, start=start, count=28))
            for n, start in enumerate(range(0, 140, 28))
        ]
        self._boot_steps = star_steps + [
            ("VOID", lambda: self._deep_space()),
            ("EARTH", lambda: self._ext_earth()),
            ("DECK", lambda: self._deck(length, hz, wide)),
            ("PORT", lambda: self._hull_side(length, -hz - 0.22, SHIP_ROSE, "s")),
            ("STARBOARD", lambda: self._hull_side(length, hz + 0.22, SHIP_WALL, "n")),
            ("VIEW", lambda: self._west_viewport(hz)),
            ("BULKHEAD", lambda: self._east_bulkhead(length, hz)),
            ("CEILING", lambda: self._ceiling(length, hz, wide)),
            ("NOSE", lambda: self._ext_nose(hz)),
            ("KEEL", lambda: self._ext_keel(length, hz)),
            ("WINGS", lambda: self._ext_wings(length, hz)),
            ("ENGINES", lambda: self._ext_engines(length, hz)),
            ("RIBS", lambda: [
                self._arch(x, IRON if (x // 12) % 2 == 0 else IRON_B) for x in range(8, int(length), 12)
            ]),
            ("BUNKS", lambda: self._ship_props(length, hz)),
            ("PADS", lambda: [self._pad(z) for z in story.SHIP_ZONES]),
            ("CREW", lambda: self._ship_people(flags)),
        ]

    def peek_boot_load(self):
        if not getattr(self, "_boot_steps", None):
            return None
        if self._boot_i >= len(self._boot_steps):
            return None
        return self._boot_steps[self._boot_i][0]

    def step_boot_load(self):
        if self._boot_i >= len(self._boot_steps):
            return False
        name, fn = self._boot_steps[self._boot_i]
        self.load_status = name
        fn()
        self._boot_i += 1
        self.load_frac = self._boot_i / max(1, len(self._boot_steps))
        return self._boot_i < len(self._boot_steps)

    def _earth(self, flags):
        from proto.config import EARTH_LEN

        left, right = 14.0, 22.0
        self._box(EARTH_SAND, (left / 2, -0.2, 0), (left + 1, 0.4, 18), collider="box")
        mid = (left + right) / 2
        self._box(EARTH_SAND, ((right + EARTH_LEN) / 2, -0.2, 0), (EARTH_LEN - right + 1, 0.4, 18), collider="box")
        self._box(EARTH_CLIFF, (mid, -2.4, 0), (right - left, 0.5, 18))
        self._box(EARTH_DIRT, (left, -0.6, 0), (0.6, 1.6, 18), collider="box")
        self._box(EARTH_CLIFF, (left - 1.2, 0.4, 0), (1.4, 1.2, 10))
        self._box(EARTH_DIRT, (right, -0.6, 0), (0.6, 1.6, 18), collider="box")
        self._box(GOLD, (32, 7.5, -11), (2.2, 2.2, 2.2))
        self._box(EARTH_CLIFF, (8, 0.9, -1.4), (3.0, 1.8, 2.4), collider="box")
        self._box(CREAM, (8, 1.95, -1.4), (2.2, 0.25, 1.6))
        if flags.get("ravine"):
            self._box((232, 196, 150), (mid, 0.22, 0), (right - left - 0.5, 0.4, 2.2), collider="box")
        for z in story.EARTH_ZONES:
            if z.key == "storm" and not flags.get("storm"):
                continue
            self._pad(z)
        for n in story.EARTH_NPCS:
            if n.show_if and not flags.get(n.show_if):
                continue
            if n.hide_if and flags.get(n.hide_if):
                continue
            self._person(n)

    def _c2(self, flags):
        from proto.config import C2_LEN

        self._box(EARTH_SAND, (C2_LEN / 2, -0.2, 0), (C2_LEN + 2, 0.4, 16), collider="box")
        self._box(GOLD, (24, 6.8, -9), (2.6, 2.6, 2.6))
        self._box(EARTH_CLIFF, (9, 0.7, 0), (2.4, 1.4, 2.4), collider="box")
        self._box(TEAL, (9, 1.5, 0), (1.4, 0.2, 1.4))
        if flags.get("shade"):
            self._box(CREAM, (9, 2.4, 0), (3.4, 0.16, 3.0))
        if flags.get("c2_elevator_done"):
            self._box(STEEL_TOTEM, (22, 3.2, 0), (0.35, 6.4, 0.35))
        for z in story.C2_ZONES:
            self._pad(z)
        for n in story.C2_NPCS:
            if n.show_if and not flags.get(n.show_if):
                continue
            if n.hide_if and flags.get(n.hide_if):
                continue
            self._person(n)

    def nearest_npc(self, player, radius=3.4):
        best = None
        best_d = radius
        for e in self.npcs:
            d = (Vec3(e.x, 0, e.z) - Vec3(player.x, 0, player.z)).length()
            if d < best_d:
                best_d = d
                best = e
        return best

    def zone_here(self, player):
        for pad in self.pads.values():
            if pad.zone.contains(player.x, player.z):
                return pad.zone
        return None

    def find_npc(self, nid):
        for e in self.npcs:
            if e.npc_id == nid:
                return e
        return None
