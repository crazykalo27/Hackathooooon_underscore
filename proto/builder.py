"""Pad builder — place parts, T runs real gravity / piston / motor tests."""

from __future__ import annotations

from ursina import Entity, Vec3, destroy, mouse, time

from proto.config import MATERIALS
from proto import sim
from proto.visuals import solid

FLOOR = 0.28
GRAVITY = 22.0
TEST_TIME = 2.6


class Builder:
    def __init__(self):
        self.active = False
        self.zone = None
        self.parts = []
        self.crate = None
        self.ghost = None
        self.drop_mark = None
        self.kind = "box"
        self.material = "wood"
        self.goal_done = False
        self.message = ""
        self.root = Entity(name="builder")
        self._i = 0
        self.testing = False
        self.test_t = 0.0
        self._homes = []

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
        self.testing = False
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
        self.testing = False
        for p in self.parts:
            destroy(p)
        self.parts.clear()
        if self.crate:
            destroy(self.crate)
            self.crate = None
        if self.drop_mark:
            destroy(self.drop_mark)
            self.drop_mark = None
        if self.ghost:
            destroy(self.ghost)
            self.ghost = None
        self.zone = None
        self.goal_done = False
        self._homes = []

    def _scale(self, kind):
        return {
            "box": (0.9, 0.9, 0.9),
            "bar": (2.2, 0.32, 0.32),
            "ball": (0.7, 0.7, 0.7),
            "piston": (0.5, 1.1, 0.5),
            "motor": (0.9, 0.45, 0.9),
            "brace": (5.6, 0.4, 0.4),
        }[kind]

    def _prep(self, e, kind, mat):
        e.kind = kind
        e.mat = mat
        e.vx = 0.0
        e.vy = 0.0
        e.vz = 0.0
        e._grounded = False
        e._h0 = e.scale_y
        e._y0 = e.y
        e.origin_y = -0.5

    def _crate_home(self):
        z = self.zone
        x = z.x
        y = FLOOR
        if z.goal == "span" and z.gap:
            x = z.gap[0] - 1.1
        elif z.goal == "roll":
            x = z.x - z.w * 0.32
        elif z.goal == "shelf":
            x = z.x + 0.4
            y = 2.6
        elif z.goal == "lift":
            x = z.x
        return Vec3(x, y, z.z)

    def _spawn_crate(self):
        pos = self._crate_home()
        self.crate = solid(
            (210, 140, 70),
            parent=self.root,
            model="cube",
            position=pos,
            scale=0.7,
            collider=None,
            origin_y=-0.5,
        )
        self._prep(self.crate, "crate", "crate")
        if self.zone.goal == "shelf":
            self.drop_mark = solid(
                (210, 186, 168),
                parent=self.root,
                model="cube",
                position=(pos.x, FLOOR, pos.z),
                scale=(0.85, 0.05, 0.85),
                collider=None,
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
        self.ghost.origin_y = -0.5

    def _floor_y(self, x, z=None):
        gap = self.zone.gap if self.zone else None
        if gap and gap[0] < x < gap[1]:
            return -2.4
        return FLOOR

    def _slot(self):
        z = self.zone
        return Vec3(z.x, FLOOR, z.z)

    def _place_point(self):
        z = self.zone
        p = mouse.world_point
        if p is None or not z or not z.contains(p.x, p.z):
            p = self._slot()
        sx, sy, sz = self._scale(self.kind)
        y = self._floor_y(p.x)
        for part in self.parts:
            if abs(part.x - p.x) < (part.scale_x + sx) * 0.45 and abs(part.z - p.z) < (part.scale_z + sz) * 0.45:
                y = max(y, sim.top_y(part))
        return Vec3(p.x, y, p.z if hasattr(p, "z") else z.z)

    def update(self):
        if not self.active:
            return
        dt = min(0.05, time.dt)
        if self.testing:
            self._step_test(dt)
            return
        if self.ghost:
            self.ghost.enabled = True
            self.ghost.position = self._place_point()
            self.ghost.scale = self._scale(self.kind)

    def place(self):
        if not self.active or self.testing:
            return
        pos = self._place_point()
        p = solid(
            MATERIALS[self.material],
            parent=self.root,
            model="sphere" if self.kind == "ball" else "cube",
            position=pos,
            scale=self._scale(self.kind),
            collider="box",
            origin_y=-0.5,
        )
        self._prep(p, self.kind, self.material)
        self.parts.append(p)
        self._i += 1
        self.message = f"Placed {self.kind} ({self.material}). T to test."

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
        if not self.active:
            return
        if not self.parts:
            self.message = "Place at least one part first."
            return
        self._restore()
        self.testing = True
        self.test_t = 0.0
        self.goal_done = False
        if self.ghost:
            self.ghost.enabled = False
        self._homes = [(self.crate.position, self.crate.scale)] if self.crate else []
        for p in self.parts:
            p._y0 = p.y
            p._h0 = p.scale_y
            p.vx = p.vy = p.vz = 0
        if self.crate:
            home = self._crate_home()
            self.crate.position = home
            self.crate.vx = self.crate.vy = self.crate.vz = 0
            if self.zone.goal == "span":
                self.crate.vx = 3.0
            if self.zone.goal == "roll":
                self.crate.vx = 0.6
        self.message = "Testing physics…"

    def _restore(self):
        for p in self.parts:
            if hasattr(p, "_h0"):
                p.scale_y = p._h0
            if hasattr(p, "_y0"):
                p.y = p._y0
            p.vx = p.vy = p.vz = 0
        if self.crate:
            self.crate.position = self._crate_home()
            self.crate.vx = self.crate.vy = self.crate.vz = 0

    def _step_test(self, dt):
        steps = 3
        step = dt / steps
        for _ in range(steps):
            self._physics_step(step)
        self.test_t += dt
        if self.test_t >= TEST_TIME:
            self._finish_test()

    def _physics_step(self, dt):
        t = self.test_t
        static = [p for p in self.parts if not sim.is_dynamic(p)]
        dyn = [e for e in list(self.parts) + ([self.crate] if self.crate else []) if sim.is_dynamic(e)]

        for p in self.parts:
            if p.kind == "piston":
                grow = min(1.0, t / 0.7) * 1.5
                p.scale_y = p._h0 + grow
            if p.kind == "motor":
                p.rotation_y += 220 * dt
                if self.crate and sim.overlap(p, self.crate, slop=0.16):
                    self.crate.vx += 14.0 * dt

        z = self.zone
        for e in dyn:
            old_y = e.y
            e.vy -= GRAVITY * dt
            e.x += e.vx * dt
            e.y += e.vy * dt
            e.z += e.vz * dt
            e._grounded = False
            floor = self._floor_y(e.x)
            if e.y < floor:
                e.y = floor
                e.vy = 0
                e._grounded = True
            sim.land_on(e, static, old_y)
            e.x = max(z.x - z.w * 0.5, min(z.x + z.w * 0.5, e.x))
            e.z = max(z.z - z.d * 0.5, min(z.z + z.d * 0.5, e.z))
            if e._grounded:
                mu = sim.props(e)["friction"]
                e.vx *= max(0.0, 1.0 - mu * 1.2 * dt)
                e.vz *= max(0.0, 1.0 - mu * 1.2 * dt)

        for p in self.parts:
            if p.kind == "piston" and self.crate and sim.xz_overlap(p, self.crate, pad=0.05):
                if self.crate.y < sim.top_y(p) + 0.05:
                    sim.set_bottom(self.crate, sim.top_y(p))
                    if self.crate.vy < 0:
                        self.crate.vy = 0
                    self.crate._grounded = True

        for d in dyn:
            for s in static:
                sim.separate(d, s)

    def _finish_test(self):
        self.testing = False
        z = self.zone
        crate = self.crate
        ok = False
        if not crate:
            ok = len(self.parts) > 0
        elif z.goal == "shelf":
            ok = crate.y > 1.05 and crate._grounded
        elif z.goal == "lift":
            ok = crate.y > z.lift_y - 0.15 and any(p.kind == "piston" for p in self.parts)
        elif z.goal == "roll":
            start = z.x - z.w * 0.32
            ok = crate.x > start + 2.2 and any(p.kind == "motor" for p in self.parts)
        elif z.goal == "span" and z.gap:
            ok = crate.x > z.gap[1] - 0.15 and crate.y > 0.15
        elif z.goal == "free":
            ok = crate.y > 0.2
        else:
            ok = crate.y > 0.2
        self.goal_done = ok
        if ok:
            self.message = "It holds! Press Enter to stamp."
        else:
            self.message = "Didn't hold — rebuild and T again."
        if self.ghost:
            self.ghost.enabled = True

    def delete_last(self):
        if self.testing:
            return
        if self.parts:
            destroy(self.parts.pop())
            self.message = "Removed last part."
            self.goal_done = False
