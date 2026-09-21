"""Pad builder — click place, T test, Enter stamp."""

from __future__ import annotations

from ursina import Entity, Vec3, destroy, mouse

from proto.config import MATERIALS
from proto.visuals import solid


class Builder:
    def __init__(self):
        self.active = False
        self.zone = None
        self.parts = []
        self.crate = None
        self.ghost = None
        self.kind = "box"
        self.material = "wood"
        self.goal_done = False
        self.message = ""
        self.root = Entity(name="builder")
        self._i = 0

    def kinds(self, flags):
        k = ["box", "bar", "ball"]
        if flags.get("first_invention") or flags.get("starter"):
            k += ["piston", "motor", "brace"]
        return k

    def mats(self, flags):
        m = ["wood", "steel"]
        for x in ("sticky", "icy", "bouncy"):
            if flags.get(x):
                m.append(x)
        return m

    def enter(self, zone, flags):
        self.leave()
        self.zone = zone
        self.active = True
        self.goal_done = False
        self._i = 0
        self.message = zone.label
        k = self.kinds(flags)
        if zone.key == "workshop":
            self.kind = "box"
        elif zone.key == "hydro" and "piston" in k:
            self.kind = "piston"
        elif zone.key == "circuit" and "motor" in k:
            self.kind = "motor"
        elif zone.key == "struct" and "brace" in k:
            self.kind = "brace"
        elif self.kind not in k:
            self.kind = k[0]
        self.material = "wood"
        self._spawn_crate()
        self._ghost()
        mouse.locked = False

    def leave(self):
        self.active = False
        for p in self.parts:
            destroy(p)
        self.parts.clear()
        if self.crate:
            destroy(self.crate)
            self.crate = None
        if self.ghost:
            destroy(self.ghost)
            self.ghost = None
        self.zone = None
        self.goal_done = False

    def _scale(self, kind):
        return {
            "box": (0.9, 0.9, 0.9),
            "bar": (2.0, 0.3, 0.3),
            "ball": (0.65, 0.65, 0.65),
            "piston": (0.45, 1.35, 0.45),
            "motor": (0.85, 0.45, 0.85),
            "brace": (1.6, 0.4, 0.4),
        }[kind]

    def _spawn_crate(self):
        z = self.zone
        x = z.x
        if z.goal == "span" and z.gap:
            x = z.gap[0] - 0.5
        elif z.goal == "roll":
            x = z.x - z.w * 0.25
        self.crate = solid(
            (210, 140, 70),
            parent=self.root,
            model="cube",
            position=(x, 0.55, z.z),
            scale=0.65,
            collider="box",
        )

    def _ghost(self):
        if self.ghost:
            destroy(self.ghost)
        self.ghost = solid(
            (*MATERIALS.get(self.material, (120, 220, 180))[:3], 150),
            parent=self.root,
            model="sphere" if self.kind == "ball" else "cube",
            scale=self._scale(self.kind),
            collider=None,
        )

    def _slot(self):
        z = self.zone
        slots = [
            (z.x - 1.1, 0.5, z.z),
            (z.x, 0.5, z.z),
            (z.x + 1.1, 0.5, z.z),
            (z.x, 1.3, z.z),
            (z.x - 0.5, 1.3, z.z),
        ]
        if self.zone.key == "hydro" and self.crate:
            return Vec3(self.crate.x, 0.75, self.crate.z)
        if self.zone.key == "circuit" and self.crate:
            return Vec3(self.crate.x + 0.3, 0.4, self.crate.z)
        if self.zone.key == "struct" and z.gap:
            return Vec3((z.gap[0] + z.gap[1]) * 0.5, 0.45, z.z)
        return Vec3(*slots[self._i % len(slots)])

    def _place_point(self):
        z = self.zone
        p = mouse.world_point
        if p is not None and z and z.contains(p.x, p.z):
            return Vec3(p.x, 0.5, p.z)
        return self._slot()

    def update(self):
        if self.active and self.ghost:
            self.ghost.position = self._place_point()
            self.ghost.scale = self._scale(self.kind)

    def place(self):
        if not self.active:
            return
        pos = self._place_point()
        p = solid(
            MATERIALS[self.material],
            parent=self.root,
            model="sphere" if self.kind == "ball" else "cube",
            position=pos,
            scale=self._scale(self.kind),
            collider="box",
        )
        p.kind = self.kind
        self.parts.append(p)
        self._i += 1
        self.message = f"Placed {self.kind}. Click the pad to add more."

    def cycle(self, flags):
        k = self.kinds(flags)
        i = k.index(self.kind) if self.kind in k else 0
        self.kind = k[(i + 1) % len(k)]
        self._ghost()

    def set_mat(self, name, flags):
        if name in self.mats(flags):
            self.material = name
            self._ghost()

    def test(self):
        if not self.active or not self.parts:
            self.message = "Place at least one part first."
            return
        z = self.zone
        # Forgiving: correct part / any support → goal done
        if z.key == "workshop":
            support = max(self.parts, key=lambda p: p.y + p.scale_y * 0.5)
            self.crate.position = Vec3(support.x, support.y + support.scale_y * 0.5 + 0.4, support.z)
            self.goal_done = True
        elif z.key == "hydro" and any(getattr(p, "kind", "") == "piston" for p in self.parts):
            self.crate.y = z.lift_y + 0.3
            self.goal_done = True
        elif z.key == "circuit" and any(getattr(p, "kind", "") == "motor" for p in self.parts):
            self.crate.x = z.x + z.w * 0.3
            self.goal_done = True
        elif z.key == "struct" and z.gap:
            self.crate.x = z.gap[1]
            self.crate.y = 0.5
            self.goal_done = True
        elif z.goal == "free":
            self.goal_done = True
        elif z.goal == "shelf":
            support = max(self.parts, key=lambda p: p.y)
            self.crate.y = support.y + 1.0
            self.goal_done = True
        elif z.goal == "span" and z.gap:
            self.crate.x = z.gap[1]
            self.goal_done = True
        else:
            self.goal_done = len(self.parts) > 0
        self.message = "It holds! Press Enter to stamp." if self.goal_done else "Not yet — try again."

    def delete_last(self):
        if self.parts:
            destroy(self.parts.pop())
            self.message = "Removed last part."
            self.goal_done = False
