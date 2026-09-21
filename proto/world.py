"""Readable 3D maps as stacked pastel solids."""

from __future__ import annotations

from ursina import Entity, Vec3, destroy, scene

from proto import story
from proto.config import (
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

    def _box(self, col, pos, scale, collider=None, face=None):
        e = solid(col, parent=self.root, model="cube", position=pos, scale=scale, collider=collider)
        if face:
            e.hull_face = face
            self.hull.append(e)
        return e

    def set_hull_hidden(self, hide):
        if not hide:
            if self._cut:
                for e in self.hull:
                    e.visible = True
                self._cut = None
            return
        key = (hide.get("n"), hide.get("s"), hide.get("e"), hide.get("w"), hide.get("ceil"))
        if key == self._cut:
            return
        self._cut = key
        for e in self.hull:
            face = getattr(e, "hull_face", None)
            e.visible = not hide.get(face, False)

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
                pos = (rng.uniform(-10, length + 10), rng.uniform(0.4, 14), rng.uniform(hz + 6, hz + 32))
            elif side == "s":
                pos = (rng.uniform(-10, length + 10), rng.uniform(0.4, 14), rng.uniform(-(hz + 32), -(hz + 6)))
            elif side == "up":
                pos = (rng.uniform(-4, length + 4), rng.uniform(HULL_CEIL + 2, 26), rng.uniform(-(hz + 8), hz + 8))
            elif side == "w":
                pos = (rng.uniform(-30, -10), rng.uniform(0.2, 16), rng.uniform(-(hz + 6), hz + 6))
            else:
                pos = (rng.uniform(length + 8, length + 30), rng.uniform(0.2, 16), rng.uniform(-(hz + 6), hz + 6))
            s = rng.choice((0.07, 0.09, 0.12, 0.16, 0.22, 0.34))
            col = STAR if rng.random() > 0.28 else STAR_DIM
            if i < start:
                continue
            self._box(col, pos, (s, s, s))

    def _star_props(self, length):
        from proto.config import HALL_HALF

        hz = HALL_HALF
        self._box(COPPER, (26, 6.2, -(hz + 12)), (5.6, 5.6, 5.6))
        self._box(PATINA, (60, 8.0, hz + 14), (2.5, 2.5, 2.5))
        self._box(BRASS, (10, 11.0, hz + 10), (1.3, 1.3, 1.3))

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
        self._box(col, (length / 2, 0.5, z), (length + 8, 1.0, 0.5), collider="box", face=face)
        self._box(BRASS, (length / 2, 1.02, z + (-0.02 if z > 0 else 0.02)), (length + 8, 0.08, 0.56), face=face)
        self._box(col, (length / 2, 3.95, z), (length + 8, 1.12, 0.5), collider="box", face=face)
        self._box(col, (length / 2, 6.3, z), (length + 8, 3.6, 0.5), collider="box", face=face)
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
        self._box(BRASS, (length / 2, 4.55, fz), (length - 6, 0.16, 0.16), face=face)
        self._box(COPPER, (length / 2, 4.78, fz), (length - 8, 0.1, 0.1), face=face)
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
        self._box(COPPER, (length / 2, HULL_CEIL - 0.35, 4.2), (length - 8, 0.14, 0.14), face="ceil")
        self._box(COPPER, (length / 2, HULL_CEIL - 0.35, -4.2), (length - 8, 0.14, 0.14), face="ceil")
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
            ("VOID", lambda: self._star_props(length)),
            ("DECK", lambda: self._deck(length, hz, wide)),
            ("PORT", lambda: self._hull_side(length, -hz - 0.22, SHIP_ROSE, "s")),
            ("STARBOARD", lambda: self._hull_side(length, hz + 0.22, SHIP_WALL, "n")),
            ("VIEW", lambda: self._west_viewport(hz)),
            ("BULKHEAD", lambda: self._east_bulkhead(length, hz)),
            ("CEILING", lambda: self._ceiling(length, hz, wide)),
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
