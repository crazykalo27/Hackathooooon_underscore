"""Toy-diorama maps: a cream rocket you can open, and cake-slice colonies."""

from __future__ import annotations

from ursina import Entity, Vec3, Vec4, destroy, scene

from proto import story
from proto.config import HULL_CEIL, SKY
from proto.figure import attach, shade
from proto.visuals import mood, solid

CREAM = (244, 236, 220)
CREAM_D = (214, 196, 168)
WOOD = (196, 146, 92)
WOOD_D = (148, 102, 64)
PLANK = (214, 170, 114)
PLANK_B = (184, 140, 88)
BLUE = (86, 138, 196)
BLUE_D = (58, 104, 164)
GLASS = (168, 220, 232)
CLAY = (204, 98, 76)
GOLD = (232, 188, 72)
LEAF = (156, 196, 86)
LEAF_D = (108, 164, 72)
DIRT = (186, 132, 86)
DIRT_D = (150, 102, 68)
SAND = (236, 210, 148)
WATER = (118, 200, 216)
ROCK = (186, 170, 148)
VOID = (22, 48, 102)
STAR = (244, 240, 220)
STAR_DIM = (140, 170, 210)
LANTERN = (255, 196, 96)
INK = (54, 48, 58)


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
        window.color = color.rgb(*(VOID if map_name == "ship" else SKY))
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
        """Drop the shell on the camera's side of a plane through the player.

        Looking down removes the roof. From the side, the near wall goes and
        the far wall stays. Past 60% of max zoom the whole ship stays opaque.
        """
        from proto.config import CAM_MAP_MIN

        if (
            cam is None
            or look is None
            or self.map_name != "ship"
            or not self.hull
            or float(dist) >= CAM_MAP_MIN - 0.5
        ):
            if self._cut != "off":
                self._cut = "off"
                for e in self.hull:
                    e.set_shader_input("cut_on", 0.0)
            return
        delta = Vec3(cam) - Vec3(look)
        if delta.length() < 0.2:
            return
        direction = delta.normalized()
        key = (
            round(direction.x, 2),
            round(direction.y, 2),
            round(direction.z, 2),
            round(float(look.x), 1),
            round(float(look.z), 1),
        )
        if key == self._cut:
            return
        self._cut = key
        point = Vec4(float(look.x), float(look.y), float(look.z), 0)
        aim = Vec4(direction.x, direction.y, direction.z, 0)
        for e in self.hull:
            e.visible = True
            e.set_shader_input("cut_on", 1.0)
            e.set_shader_input("cut_point", point)
            e.set_shader_input("cut_dir", aim)

    def _span_x(self, col, y, z, x0, x1, h, d, face=None, collider=None, bay=8.0, rot=None):
        x = x0
        while x < x1 - 0.02:
            w = min(bay, x1 - x)
            self._box(col, (x + w * 0.5, y, z), (w, h, d), collider=collider, face=face, rot=rot)
            x += bay

    def _starfield(self, length):
        import random

        rng = random.Random(21)
        for _ in range(70):
            pos = (
                rng.uniform(-40, length + 40),
                rng.uniform(6, 48),
                rng.uniform(-80, 80),
            )
            if abs(pos[2]) < 24 and 0 < pos[0] < length and pos[1] < 18:
                continue
            s = rng.choice((0.18, 0.28, 0.4, 0.7))
            self._orb(STAR if rng.random() > 0.4 else STAR_DIM, pos, s)

    def _deep_space(self):
        import random

        rng = random.Random(77)
        for _ in range(36):
            pos = (rng.uniform(-180, 240), rng.uniform(-40, 120), rng.uniform(-200, 200))
            if abs(pos[0] - 40) < 70 and abs(pos[2]) < 50:
                continue
            self._orb(STAR if rng.random() > 0.5 else STAR_DIM, pos, rng.choice((1.2, 1.8, 2.6)))
        self._orb(LANTERN, (210, 90, 240), 14)
        self._orb(GOLD, (218, 94, 248), 6)

    def _ext_earth(self):
        c = (36, -150, -70)
        self._orb((72, 168, 214), c, 210)
        self._orb(LEAF, (c[0] + 24, c[1] + 72, c[2] + 18), 78)
        self._orb(LEAF_D, (c[0] - 30, c[1] + 64, c[2] - 16), 56)
        self._orb(SAND, (c[0] + 8, c[1] + 58, c[2] - 28), 40)
        self._orb(CREAM, (c[0] - 6, c[1] + 96, c[2] + 6), 48)
        self._orb((236, 244, 252), (c[0] + 22, c[1] + 88, c[2] - 8), 28)

    def _window(self, x, z, w=2.6, h=1.7, y=3.15, face=None):
        inward = -0.16 if z > 0 else 0.16
        fz = z + inward
        self._box(WOOD, (x - w * 0.5, y, fz), (0.16, h, 0.22), face=face)
        self._box(WOOD, (x + w * 0.5, y, fz), (0.16, h, 0.22), face=face)
        self._box(WOOD, (x, y + h * 0.5, fz), (w, 0.16, 0.22), face=face)
        self._box(WOOD, (x, y - h * 0.5, fz), (w, 0.16, 0.22), face=face)
        self._box(GLASS, (x, y, fz), (w - 0.2, h - 0.2, 0.1), face=face)
        self._box(WOOD_D, (x, y, fz), (0.08, h - 0.2, 0.12), face=face)

    def _hull_side(self, length, z, face):
        outer = 0.22 if z > 0 else -0.22
        inward = -0.34 if z > 0 else 0.34
        x0, x1 = -5.0, length + 5.0
        self._span_x(WOOD, 0.5, z, x0, x1, 1.0, 0.72, face=face, collider="box")
        self._span_x(CREAM, 6.2, z, x0, x1, 3.6, 0.58, face=face, collider="box")
        self._span_x(BLUE, 4.55, z + outer, x0 + 1, x1 - 1, 0.32, 0.2, face=face)
        self._span_x(GOLD, 1.08, z + outer * 0.5, x0 + 1, x1 - 1, 0.1, 0.16, face=face)
        win_w = 2.6
        windows = [7.0 + i * 11.0 for i in range(max(1, int((length - 10) / 11.0)))]
        prev = x0
        for wx in windows:
            left = wx - win_w * 0.5
            pier = left - prev
            if pier > 0.35:
                self._box(CREAM, ((prev + left) * 0.5, 3.15, z), (pier, 2.5, 0.58), collider="box", face=face)
            self._window(wx, z, w=win_w, face=face)
            prev = wx + win_w * 0.5
        if x1 - prev > 0.35:
            self._box(CREAM, ((prev + x1) * 0.5, 3.15, z), (x1 - prev, 2.5, 0.58), collider="box", face=face)
        for x in range(4, int(length), 8):
            self._box(WOOD, (x, 3.8, z + inward), (0.26, 6.6, 0.3), face=face)
        for x in range(12, int(length), 18):
            self._box(CLAY, (x, 1.2, z + inward * 0.7), (0.85, 0.14, 0.32), face=face)
            self._orb(LEAF, (x - 0.22, 1.5, z + inward * 0.7), 0.2, face=face)
            self._orb(LEAF_D, (x + 0.2, 1.42, z + inward * 0.7), 0.14, face=face)

    def _deck(self, length, hz, wide):
        self._box(DIRT_D, (length / 2, -0.55, 0), (length + 8, 0.7, wide), collider="box")
        tw, td = 3.6, 3.8
        zi = -hz + 1.6
        row = 0
        while zi < hz - 1.2:
            xi = 0.0
            col = 0
            while xi < length - 1:
                # leave the brace bay open so the pit reads
                if 64.8 < xi < 71.2:
                    xi += tw
                    col += 1
                    continue
                plate = PLANK if (row + col) % 2 == 0 else PLANK_B
                self._box(plate, (xi + tw * 0.5, 0.05, zi + td * 0.5), (tw - 0.12, 0.1, td - 0.12))
                xi += tw
                col += 1
            zi += td
            row += 1
        self._box(CREAM, (32, 0.12, 0), (60, 0.06, 2.4))
        self._box(DIRT, (68, -1.15, 0), (5.4, 2.0, 7.2))
        self._box(ROCK, (65.4, -0.2, 0), (0.35, 1.6, 7.2))
        self._box(ROCK, (70.6, -0.2, 0), (0.35, 1.6, 7.2))

    def _ceiling(self, length, hz, wide):
        self._span_x(CREAM, HULL_CEIL, 0, -1.0, length + 2.0, 0.32, wide - 1.4, face="ceil", bay=6.0)
        for x in range(6, int(length), 8):
            self._box(WOOD, (x, HULL_CEIL - 0.28, 0), (0.32, 0.28, wide - 2.4), face="ceil")
            self._box(WOOD, (x, HULL_CEIL - 0.85, 0), (0.08, 0.7, 0.08), face="ceil")
            self._orb(LANTERN, (x, HULL_CEIL - 1.25, 0), 0.32, face="ceil")
            self._orb(GOLD, (x, HULL_CEIL - 1.28, 0), 0.16, face="ceil")

    def _arch(self, x):
        from proto.config import HALL_HALF

        z = HALL_HALF - 0.55
        self._box(WOOD, (x, 3.7, -z), (0.5, 7.0, 0.42), face="s")
        self._box(WOOD, (x, 3.7, z), (0.5, 7.0, 0.42), face="n")
        self._box(WOOD, (x, 7.35, 0), (0.5, 0.42, HALL_HALF * 2 - 0.4), face="ceil")
        self._box(GOLD, (x, 7.05, 0), (0.62, 0.1, HALL_HALF * 2 - 1.2), face="ceil")

    def _west_viewport(self, hz):
        wide = hz * 2 + 0.8
        gap = 5.4
        side = (wide - gap) * 0.5
        zc = gap * 0.5 + side * 0.5
        self._box(CREAM, (-4.4, 0.55, 0), (0.55, 1.1, wide), collider="box", face="w")
        self._box(CREAM, (-4.4, 6.3, 0), (0.55, 3.6, wide), collider="box", face="w")
        self._box(CREAM, (-4.4, 3.15, -zc), (0.55, 4.1, side), collider="box", face="w")
        self._box(CREAM, (-4.4, 3.15, zc), (0.55, 4.1, side), collider="box", face="w")
        self._box(WOOD, (-4.15, 3.2, -gap * 0.5), (0.22, 4.0, 0.2), face="w")
        self._box(WOOD, (-4.15, 3.2, gap * 0.5), (0.22, 4.0, 0.2), face="w")
        self._box(WOOD, (-4.15, 5.15, 0), (0.22, 0.2, gap), face="w")
        self._box(WOOD, (-4.15, 1.2, 0), (0.22, 0.2, gap), face="w")
        self._box(GLASS, (-4.45, 3.15, 0), (0.12, 3.6, gap - 0.4), face="w")
        self._box(BLUE, (-4.7, 6.9, 0), (0.3, 0.35, 3.2), face="w")

    def _east_bulkhead(self, length, hz):
        wide = hz * 2 + 0.8
        x = length + 3.8
        door = 2.4
        side = (wide - door) * 0.5
        zc = door * 0.5 + side * 0.5
        self._box(CREAM, (x, 0.5, 0), (0.55, 1.0, wide), collider="box", face="e")
        self._box(CREAM, (x, 5.6, 0), (0.55, 5.0, wide), collider="box", face="e")
        self._box(CREAM, (x, 2.35, -zc), (0.55, 2.7, side), collider="box", face="e")
        self._box(CREAM, (x, 2.35, zc), (0.55, 2.7, side), collider="box", face="e")
        self._box(WOOD, (x - 0.4, 1.45, -door * 0.5), (0.18, 2.5, 0.16), face="e")
        self._box(WOOD, (x - 0.4, 1.45, door * 0.5), (0.18, 2.5, 0.16), face="e")
        self._box(WOOD, (x - 0.4, 2.65, 0), (0.18, 0.16, door), face="e")
        self._box(BLUE, (x - 0.15, 1.5, 0), (0.08, 2.2, 1.5), face="e")

    def _ext_nose(self, hz):
        self._orb(CREAM, (-14, 3.5, 0), (12, 7.2, 16), face="w")
        self._orb(CREAM_D, (-20, 2.4, 0), (8, 4.0, 7), face="w")
        self._orb(CREAM, (-25, 1.7, 0), (5.5, 2.4, 3.6), face="w")
        self._orb(CLAY, (-28.2, 1.45, 0), (2.6, 1.5, 2.0), face="w")
        self._orb(GOLD, (-29.6, 1.45, 0), 0.7, face="w")
        self._box(BLUE, (-16, 5.6, 0), (7, 0.4, 8), face="w")
        self._orb(GLASS, (-11.5, 5.4, 0), (3.6, 2.0, 5.5), face="w")
        for s in (-1, 1):
            face = "n" if s > 0 else "s"
            self._box(BLUE, (-15, 1.15, s * (hz + 2.5)), (7.5, 0.32, 5.5), rot=(0, s * 16, s * 7), face=face)
            self._box(CREAM, (-15, 1.32, s * (hz + 2.5)), (5, 0.1, 3.2), rot=(0, s * 16, s * 7), face=face)

    def _ext_shell(self, length, hz):
        x = 0.0
        while x < length - 6:
            self._orb(CREAM, (x + 7, 10.6, 0), (14, 4.8, hz * 1.25), face="ceil")
            self._box(BLUE, (x + 7, 12.5, 0), (7.5, 0.45, 2.4), face="ceil")
            x += 13.0
        self._orb(CREAM_D, (length * 0.48, -2.4, 0), (length * 0.62, 3.4, 15))
        self._box(BLUE, (length * 0.48, -1.15, 0), (length * 0.4, 0.4, 1.5))
        self._box(GOLD, (length * 0.48, -1.0, 0), (length * 0.22, 0.12, 0.5))

    def _ext_wings(self, length, hz):
        for s in (-1.0, 1.0):
            face = "n" if s > 0 else "s"
            z0 = s * hz
            self._box(BLUE, (46, 1.15, z0 + s * 9), (26, 0.6, 16), rot=(s * 5, s * 20, s * 3), face=face)
            self._box(CREAM, (54, 1.4, z0 + s * 14), (16, 0.22, 9), rot=(s * 5, s * 24, s * 3), face=face)
            self._box(BLUE_D, (62, 0.85, z0 + s * 18), (12, 0.4, 7), rot=(s * 4, s * 28, 0), face=face)
            self._orb(GOLD, (70, 1.2, z0 + s * 22), 0.85, face=face)
            self._orb(CLAY, (72.2, 1.2, z0 + s * 23.2), 0.45, face=face)
            for x in (36, 48, 60):
                self._orb(GOLD, (x, 1.45, z0 + s * 1.4), 0.32, face=face)

    def _ext_engines(self, length, hz):
        aft = length + 9
        for z, y, k in ((0.0, 2.6, 1.2), (6.4, 1.45, 0.78), (-6.4, 1.45, 0.78)):
            self._orb(CREAM, (aft - 2.2, y, z), (6.2 * k, 3.4 * k, 3.4 * k), face="e")
            self._orb(BLUE, (aft + 1.4, y, z), (2.4 * k, 3.8 * k, 3.8 * k), face="e")
            self._orb(CLAY, (aft + 3.2, y, z), (2.2 * k, 2.6 * k, 2.6 * k), face="e")
            self._orb(LANTERN, (aft + 4.8, y, z), (1.5 * k, 1.9 * k, 1.9 * k), face="e")
            self._orb(GOLD, (aft + 6.0, y, z), (0.7 * k, 1.0 * k, 1.0 * k), face="e")
        self._box(BLUE, (length + 1.5, 9.2, 0), (5.5, 4.2, 0.5), face="ceil")
        self._box(GOLD, (length + 1.2, 11.0, 0), (2.0, 0.7, 0.55), face="ceil")
        self._box(CREAM, (length + 4, 6.6, 0), (3.2, 0.28, 6), face="e")

    def _bed(self, x, z):
        self._box(WOOD_D, (x, 0.28, z), (2.3, 0.36, 1.15))
        self._box(CREAM, (x, 0.52, z), (2.1, 0.16, 1.0))
        self._box(BLUE, (x + 0.15, 0.62, z), (1.35, 0.1, 0.82))
        self._box(CREAM, (x - 0.78, 0.72, z), (0.42, 0.18, 0.36))

    def _table(self, x, z):
        self._box(WOOD, (x, 0.74, z), (1.7, 0.1, 0.95))
        for dx, dz in ((-0.62, -0.32), (0.62, -0.32), (-0.62, 0.32), (0.62, 0.32)):
            self._box(WOOD_D, (x + dx, 0.36, z + dz), (0.1, 0.68, 0.1))
        self._orb(CLAY, (x + 0.35, 0.9, z), 0.14)
        self._box(CREAM, (x - 0.3, 0.84, z + 0.1), (0.28, 0.06, 0.22))

    def _barrel(self, x, z):
        self._orb(WOOD, (x, 0.4, z), (0.48, 0.72, 0.48))
        self._orb(WOOD_D, (x, 0.62, z), (0.52, 0.1, 0.52))
        self._orb(WOOD_D, (x, 0.2, z), (0.52, 0.1, 0.52))

    def _crate(self, x, z, s=0.72, col=None):
        col = col or WOOD
        self._box(col, (x, s * 0.5, z), (s, s, s))
        self._box(WOOD_D, (x, s * 0.5, z), (s * 1.02, 0.07, 0.08))

    def _pot(self, x, z, h=1.0):
        self._orb(CLAY, (x, 0.22 * h, z), (0.32 * h, 0.36 * h, 0.32 * h))
        self._orb(LEAF, (x, 0.58 * h, z), 0.4 * h)
        self._orb(LEAF_D, (x + 0.12 * h, 0.5 * h, z + 0.06 * h), 0.24 * h)

    def _tank(self, x, z, liquid=BLUE):
        self._box(WOOD, (x, 0.12, z), (1.5, 0.2, 1.5))
        self._orb(CREAM, (x, 0.95, z), (1.25, 1.5, 1.25))
        self._orb(liquid, (x, 0.75, z), (0.85, 0.85, 0.85))
        self._box(GOLD, (x, 1.75, z), (0.16, 0.4, 0.16))
        self._orb(GOLD, (x, 1.95, z), 0.14)

    def _console(self, x, z, col):
        self._box(CREAM_D, (x, 0.65, z), (1.7, 1.15, 0.7))
        self._box(col, (x, 1.15, z + 0.28), (1.3, 0.45, 0.12))
        self._orb(GOLD, (x - 0.4, 0.78, z + 0.38), 0.1)
        self._orb(LEAF, (x, 0.78, z + 0.38), 0.1)
        self._orb(CLAY, (x + 0.4, 0.78, z + 0.38), 0.1)

    def _elevator(self, x):
        self._box(GOLD, (x, 0.12, 0), (2.6, 0.16, 2.6))
        self._box(CREAM, (x, 1.55, 0), (2.15, 2.9, 2.15))
        self._box(BLUE, (x, 3.15, 0), (2.4, 0.22, 2.4))
        self._box(GLASS, (x, 1.7, 1.1), (1.15, 1.35, 0.08))
        self._orb(LANTERN, (x, 3.45, 0), 0.22)
        self._box(WOOD, (x, 1.6, -1.1), (0.7, 1.3, 0.08))

    def _ship_props(self, length, hz):
        self._box(BLUE, (6, 0.08, -6), (6.5, 0.04, 4.2))
        self._bed(3.4, -9.6)
        self._bed(3.4, -7.2)
        self._crate(1.4, -11.4, 0.6)
        self._crate(1.9, -11.2, 0.45, CREAM)
        self._pot(6.5, -11.6)
        self._table(11.5, 10.6)
        self._barrel(13.2, 11.4)
        self._barrel(14.0, 11.0)
        self._pot(8.2, 12.0)
        self._box(WOOD, (16.5, 1.3, -12.2), (0.22, 2.2, 2.4))
        self._box(GOLD, (16.7, 1.7, -12.6), (0.08, 0.7, 0.08))
        self._box(BLUE, (16.7, 1.5, -11.8), (0.08, 0.45, 0.08))
        for x, col in ((30, (96, 176, 220)), (44, (96, 176, 220))):
            self._tank(x, 10.4, col)
            self._tank(x, -10.4, col)
        self._span_x(BLUE, 2.4, 11.6, 28, 48, 0.16, 0.16)
        self._span_x(BLUE, 2.4, -11.6, 28, 48, 0.16, 0.16)
        self._console(48, 11.2, (120, 196, 148))
        self._console(56, -11.2, (120, 196, 148))
        self._crate(60.5, 10.8, 0.8)
        self._crate(61.2, 11.3, 0.55)
        self._box(WOOD, (66, 0.9, 9.5), (1.2, 1.6, 0.2))
        self._box(WOOD, (70, 0.9, -9.5), (1.2, 1.6, 0.2))
        self._box(GOLD, (68, 0.2, 8.2), (4.6, 0.08, 0.2))
        self._box(GOLD, (68, 0.2, -8.2), (4.6, 0.08, 0.2))
        self._table(78, -10.2)
        self._pot(80.5, -11.5)
        self._crate(84, 11, 0.7, CREAM_D)
        self._elevator(length - 4.2)
        for x in (18, 34, 58, 76):
            self._pot(x, 12.4, 0.85)

    def _ship(self, flags):
        from proto.config import HALL_HALF, SHIP_LEN

        length = SHIP_LEN
        hz = HALL_HALF
        wide = hz * 2 + 0.8
        self._starfield(length)
        self._deep_space()
        self._ext_earth()
        self._deck(length, hz, wide)
        self._hull_side(length, -hz - 0.15, "s")
        self._hull_side(length, hz + 0.15, "n")
        self._west_viewport(hz)
        self._east_bulkhead(length, hz)
        self._ceiling(length, hz, wide)
        self._ext_nose(hz)
        self._ext_shell(length, hz)
        self._ext_wings(length, hz)
        self._ext_engines(length, hz)
        for x in range(12, int(length), 16):
            self._arch(x)
        self._ship_props(length, hz)
        for z in story.SHIP_ZONES:
            self._pad(z)
        self._ship_people(flags)

    def _person(self, defn):
        root = Entity(parent=self.root, position=(defn.x, 0, defn.z), rotation_y=defn.rot)
        Entity(
            parent=root,
            model="cube",
            position=(0, 0.85, 0),
            scale=(0.55, 1.7, 0.45),
            collider="box",
            visible=False,
        )
        look = sum(ord(c) for c in defn.id)
        attach(
            root,
            shirt=defn.color,
            pants=shade(defn.color, 0.7),
            hair=shade(defn.color, 0.42),
            accent=defn.color,
            look=look,
        )
        root.npc_id = defn.id
        root.npc_name = defn.name
        root.talk_id = defn.talk
        self.npcs.append(root)
        return root

    def _pad(self, zone):
        rim = WOOD
        if zone.gap:
            left, right = zone.gap
            lw = max(1.2, left - (zone.x - zone.w * 0.5))
            rw = max(1.2, (zone.x + zone.w * 0.5) - right)
            self._box(rim, ((zone.x - zone.w * 0.5) + lw * 0.5, 0.1, zone.z), (lw + 0.3, 0.16, zone.d + 0.25))
            self._box(zone.color, ((zone.x - zone.w * 0.5) + lw * 0.5, 0.22, zone.z), (lw * 0.86, 0.1, zone.d * 0.86))
            self._box(rim, ((zone.x + zone.w * 0.5) - rw * 0.5, 0.1, zone.z), (rw + 0.3, 0.16, zone.d + 0.25))
            pad = self._box(zone.color, ((zone.x + zone.w * 0.5) - rw * 0.5, 0.22, zone.z), (rw * 0.86, 0.1, zone.d * 0.86))
        else:
            self._box(rim, (zone.x, 0.1, zone.z), (zone.w + 0.35, 0.16, zone.d + 0.35))
            pad = self._box(zone.color, (zone.x, 0.22, zone.z), (zone.w * 0.9, 0.1, zone.d * 0.9))
            self._box(CREAM, (zone.x, 0.3, zone.z), (zone.w * 0.2, 0.04, zone.d * 0.2))
        pad.zone = zone
        self.pads[zone.key] = pad
        return pad

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
        window.color = color.rgb(*VOID)
        mood("ship")
        length = SHIP_LEN
        hz = HALL_HALF
        wide = hz * 2 + 0.8
        self._boot_i = 0
        self.load_status = "stars"
        self.load_frac = 0.0
        self._boot_steps = [
            ("stars", lambda: self._starfield(length)),
            ("sky", self._deep_space),
            ("planet", self._ext_earth),
            ("deck", lambda: self._deck(length, hz, wide)),
            ("port", lambda: self._hull_side(length, -hz - 0.15, "s")),
            ("starboard", lambda: self._hull_side(length, hz + 0.15, "n")),
            ("cockpit", lambda: self._west_viewport(hz)),
            ("airlock", lambda: self._east_bulkhead(length, hz)),
            ("ceiling", lambda: self._ceiling(length, hz, wide)),
            ("nose", lambda: self._ext_nose(hz)),
            ("shell", lambda: self._ext_shell(length, hz)),
            ("wings", lambda: self._ext_wings(length, hz)),
            ("engines", lambda: self._ext_engines(length, hz)),
            ("ribs", lambda: [self._arch(x) for x in range(12, int(length), 16)]),
            ("rooms", lambda: self._ship_props(length, hz)),
            ("pads", lambda: [self._pad(z) for z in story.SHIP_ZONES]),
            ("crew", lambda: self._ship_people(flags)),
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

    def _cake(self, x, z, w, d, top=LEAF, side=DIRT):
        self._box(side, (x, -0.7, z), (w, 1.5, d))
        self._box(DIRT_D, (x, -0.15, z), (w + 0.15, 0.35, d + 0.15))
        self._box(top, (x, 0.08, z), (w - 0.35, 0.16, d - 0.35), collider="box")

    def _tree(self, x, z, h=1.0):
        self._box(WOOD_D, (x, 0.55 * h, z), (0.22 * h, 1.1 * h, 0.22 * h))
        self._orb(LEAF, (x, 1.45 * h, z), 0.85 * h)
        self._orb(LEAF_D, (x + 0.28 * h, 1.2 * h, z + 0.1 * h), 0.5 * h)
        self._orb(shade(LEAF, 1.08), (x - 0.18 * h, 1.7 * h, z - 0.08 * h), 0.42 * h)

    def _palm(self, x, z):
        self._box(WOOD, (x, 1.15, z), (0.18, 2.2, 0.18))
        self._orb(LEAF, (x, 2.35, z), (1.15, 0.42, 1.15))
        self._orb(LEAF_D, (x + 0.35, 2.15, z + 0.1), 0.4)
        self._orb(shade(LEAF, 1.05), (x - 0.3, 2.45, z - 0.05), 0.32)

    def _cottage(self, x, z):
        self._box(CREAM, (x, 1.05, z), (2.5, 1.9, 2.2))
        self._box(CLAY, (x, 2.25, z - 0.4), (2.9, 0.18, 1.55), rot=(32, 0, 0))
        self._box(CLAY, (x, 2.25, z + 0.4), (2.9, 0.18, 1.55), rot=(-32, 0, 0))
        self._box(WOOD_D, (x, 0.7, z + 1.12), (0.55, 1.15, 0.1))
        self._box(GLASS, (x - 0.7, 1.25, z + 1.12), (0.4, 0.4, 0.08))
        self._box(GLASS, (x + 0.7, 1.25, z + 1.12), (0.4, 0.4, 0.08))
        self._box(CREAM_D, (x + 0.75, 2.7, z - 0.2), (0.28, 0.7, 0.28))
        self._box(WOOD, (x, 0.15, z + 1.5), (1.1, 0.12, 0.45))

    def _windmill(self, x, z):
        self._box(CREAM, (x, 1.7, z), (1.5, 3.3, 1.5))
        self._box(CLAY, (x, 3.5, z), (2.0, 0.22, 2.0))
        self._orb(WOOD, (x, 2.5, z + 0.85), 0.32)
        self._box(WOOD, (x, 2.5, z + 0.95), (0.16, 2.5, 0.08))
        self._box(WOOD, (x, 2.5, z + 0.95), (2.5, 0.16, 0.08))
        self._box(GLASS, (x, 1.4, z + 0.78), (0.4, 0.45, 0.08))

    def _rock(self, x, z, s=1.0):
        self._orb(ROCK, (x, 0.35 * s, z), (1.1 * s, 0.7 * s, 0.9 * s))
        self._orb(CREAM_D, (x + 0.2 * s, 0.55 * s, z), 0.35 * s)

    def _critter(self, x, z, col):
        self._orb(col, (x, 0.28, z), (0.5, 0.36, 0.62))
        self._orb(col, (x + 0.22, 0.48, z + 0.16), 0.26)
        self._orb(INK, (x + 0.28, 0.52, z + 0.26), 0.06)
        self._orb(INK, (x + 0.16, 0.52, z + 0.28), 0.06)
        self._box(col, (x - 0.28, 0.32, z), (0.2, 0.08, 0.08))

    def _cloud(self, x, y, z, s=1.0):
        self._orb(CREAM, (x, y, z), (2.2 * s, 0.7 * s, 1.2 * s))
        self._orb(CREAM, (x + 0.8 * s, y + 0.15 * s, z), (1.4 * s, 0.6 * s, 0.9 * s))

    def _scatter_people(self, npcs, flags):
        for n in npcs:
            if n.show_if and not flags.get(n.show_if):
                continue
            if n.hide_if and flags.get(n.hide_if):
                continue
            self._person(n)

    def _earth(self, flags):
        from proto.config import EARTH_LEN

        self._box(WATER, (EARTH_LEN / 2, -1.7, 0), (EARTH_LEN + 36, 0.5, 42))
        self._cake(7.2, 0, 16, 16, SAND, DIRT)
        self._cake(34, 0, EARTH_LEN - 20, 16, LEAF, DIRT)
        self._box(DIRT, (18, -1.5, 0), (8, 1.2, 14))
        self._box(ROCK, (14.2, -0.2, 0), (0.7, 2.2, 14))
        self._box(ROCK, (21.8, -0.2, 0), (0.7, 2.2, 14))
        self._box(WATER, (18, -1.85, 0), (6.5, 0.35, 10))
        if flags.get("ravine"):
            self._box(WOOD, (18, 0.28, 0), (8.2, 0.22, 2.4), collider="box")
            self._box(WOOD_D, (18, 0.5, -1.15), (8.2, 0.18, 0.12))
            self._box(WOOD_D, (18, 0.5, 1.15), (8.2, 0.18, 0.12))
        self._cottage(6.2, -6.4)
        self._windmill(30, -6.2)
        self._rock(3.2, 5.5, 1.1)
        self._rock(12.5, 6.2, 0.7)
        self._rock(40, 6.4, 0.9)
        for x, z, h in (
            (2.4, -6.8, 1.1),
            (10.5, 6.6, 0.85),
            (26, 6.8, 1.2),
            (36, -6.6, 1.0),
            (44, 5.8, 1.3),
            (28, -6.9, 0.75),
        ):
            self._tree(x, z, h)
        self._palm(42, -5.5)
        x = 1.2
        while x < EARTH_LEN - 1:
            if not 13.5 < x < 22.5:
                self._box(SAND, (x, 0.18, 0), (1.5, 0.06, 1.5))
            x += 2.1
        self._critter(9.5, 5.4, (196, 140, 84))
        self._cloud(-6, 11, -8, 1.3)
        self._cloud(24, 13, 10, 1.6)
        self._cloud(48, 12, -12, 1.1)
        for z in story.EARTH_ZONES:
            if z.key == "storm" and not flags.get("storm"):
                continue
            self._pad(z)
        self._scatter_people(story.EARTH_NPCS, flags)

    def _c2(self, flags):
        from proto.config import C2_LEN

        self._box(WATER, (C2_LEN / 2, -1.7, 0), (C2_LEN + 28, 0.5, 36))
        self._cake(C2_LEN / 2, 0, C2_LEN + 2, 15, LEAF, DIRT)
        self._tank(8.2, 6.3, (80, 190, 180))
        self._tank(11.4, 6.6, (120, 210, 200))
        if flags.get("shade"):
            self._box(CREAM, (9.8, 2.7, 6.4), (4.6, 0.12, 3.2))
            self._box(WOOD, (7.8, 1.4, 6.4), (0.12, 2.6, 0.12))
            self._box(WOOD, (11.8, 1.4, 6.4), (0.12, 2.6, 0.12))
        if flags.get("c2_elevator_done"):
            self._box(CREAM, (22, 2.2, 0), (1.3, 4.2, 1.3))
            self._box(BLUE, (22, 4.5, 0), (1.8, 0.4, 1.8))
            self._orb(GOLD, (22, 5.0, 0), 0.35)
        self._palm(3.2, 5.5)
        self._palm(4.4, -5.6)
        self._tree(18, 6.2, 0.9)
        self._tree(32, -5.8, 1.1)
        self._rock(16, -6, 0.8)
        self._critter(6, -5.2, (232, 168, 96))
        self._cloud(8, 12, 8, 1.2)
        self._cloud(30, 11, -9, 1.0)
        x = 1.5
        while x < C2_LEN:
            if not (23 < x < 29):
                self._box(SAND, (x, 0.18, 0), (1.4, 0.06, 1.3))
            x += 2.2
        for z in story.C2_ZONES:
            self._pad(z)
        self._scatter_people(story.C2_NPCS, flags)

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
