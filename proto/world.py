"""Readable 3D maps as stacked pastel solids."""

from __future__ import annotations

from ursina import Entity, Text, Vec3, destroy, scene

from proto import story
from proto.config import (
    ACCENT,
    CREAM,
    EARTH_CLIFF,
    EARTH_DIRT,
    EARTH_SAND,
    GOLD,
    INK,
    SHADOW,
    SHIP_FLOOR,
    SHIP_FLOOR_B,
    SHIP_ROSE,
    SHIP_WALL,
    TEAL,
    rgb,
)
from proto.figure import attach, shade
from proto.visuals import solid

INK_SLAB = (72, 58, 68)
STEEL_TOTEM = (176, 188, 204)


class World:
    def __init__(self):
        self.root = None
        self.npcs = []
        self.pads = {}
        self.map_name = "ship"

    def clear(self):
        if self.root:
            destroy(self.root)
        self.root = Entity()
        self.npcs.clear()
        self.pads.clear()

    def load(self, map_name: str, flags: dict):
        self.clear()
        self.map_name = map_name
        scene.fog_density = 0
        if map_name == "ship":
            self._ship(flags)
        elif map_name == "c2":
            self._c2(flags)
        else:
            self._earth(flags)

    def _box(self, col, pos, scale, collider=None):
        return solid(col, parent=self.root, model="cube", position=pos, scale=scale, collider=collider)

    def _arch(self, x, col=SHIP_WALL):
        from proto.config import HALL_HALF

        z = HALL_HALF - 0.35
        self._box(col, (x, 2.15, -z), (0.5, 4.3, 0.5))
        self._box(col, (x, 2.15, z), (0.5, 4.3, 0.5))
        self._box(col, (x, 4.4, 0), (0.5, 0.4, HALL_HALF * 2))

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
        self._name_tag(root, defn.name)
        self.npcs.append(root)
        return root

    def _name_tag(self, root, name):
        holder = Entity(parent=root, y=2.14)
        holder.world_rotation = Vec3(0, 0, 0)
        holder.billboard = True
        w = max(0.72, 0.15 * len(name) + 0.28)
        solid(CREAM, parent=holder, model="quad", scale=(w, 0.26), z=0.02)
        Text(
            text=name,
            parent=holder,
            origin=(0, 0),
            scale=11,
            color=rgb(INK),
        )

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
        self._box(SHIP_FLOOR, (length / 2, -0.22, 0), (length + 10, 0.44, wide), collider="box")
        for i, x in enumerate(range(-4, int(length), 4)):
            tile = SHIP_FLOOR if i % 2 == 0 else SHIP_FLOOR_B
            self._box(tile, (x + 2, 0.01, 0), (3.7, 0.05, wide - 0.8))
        self._box(SHIP_ROSE, (length / 2, 0.55, -hz - 0.2), (length + 10, 1.1, 0.35), collider="box")
        self._box(SHIP_WALL, (length / 2, 0.55, hz + 0.2), (length + 10, 1.1, 0.35), collider="box")
        self._box(SHIP_WALL, (-4.5, 2.0, 0), (0.5, 4.0, wide), collider="box")
        self._box(ACCENT, (-4.5, 4.2, 0), (0.6, 0.35, 3.2))
        for x in range(8, int(length), 12):
            self._arch(x, SHIP_WALL if (x // 12) % 2 == 0 else CREAM)
        for x in range(2, int(length), 10):
            self._box((168, 204, 220), (x, 2.15, -hz - 0.25), (1.6, 1.3, 0.12))
            self._box(GOLD, (x + 5, 2.8, hz + 0.25), (0.9, 0.18, 0.18))
        self._box(SHIP_ROSE, (3.2, 0.35, -2.2), (3.2, 0.7, 2.0), collider="box")
        self._box(CREAM, (2.4, 0.78, -2.2), (1.4, 0.18, 1.5))
        self._box(ACCENT, (4.4, 0.85, -2.2), (0.35, 0.35, 0.35))
        self._box(INK_SLAB, (10.5, 1.6, -hz + 0.35), (2.2, 1.5, 0.16))
        self._box(GOLD, (10.5, 1.6, -hz + 0.45), (1.4, 0.9, 0.08))
        self._box((196, 140, 100), (14, 0.4, -hz + 1.6), (2.4, 0.8, 1.0), collider="box")
        self._box(CREAM, (14, 0.85, -hz + 1.6), (2.5, 0.1, 1.1))
        ex = length - 3.5
        self._box(SHIP_ROSE, (ex, 1.2, 0), (2.2, 2.4, 2.2), collider="box")
        self._box(ACCENT, (ex, 2.6, 0), (1.4, 0.4, 1.4))
        self._box(CREAM, (ex, 3.4, 0), (0.7, 1.2, 0.7))
        self._box((210, 228, 236), (16, 6.4, -hz - 3), (1.4, 1.4, 1.4))
        self._box((232, 200, 186), (40, 7.2, hz + 3), (0.9, 0.9, 0.9))
        self._box((176, 208, 196), (70, 6.8, -hz - 2), (1.1, 1.1, 1.1))
        for z in story.SHIP_ZONES:
            self._pad(z)
        for n in story.SHIP_NPCS:
            if n.show_if and not flags.get(n.show_if):
                continue
            if n.hide_if and flags.get(n.hide_if):
                continue
            self._person(n)

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
