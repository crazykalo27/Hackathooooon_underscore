"""Pad builder — place, stroke-to-beam, weld/confirm, gravity test, blueprints."""

from __future__ import annotations

from ursina import Entity, Vec3, destroy, mouse, time

from proto.config import MATERIALS
from proto import sim
from proto.visuals import solid

FLOOR = 0.28
GRAVITY = 22.0
TEST_TIME = 2.8

STARTER_PARTS = {
    "hydraulics": ("piston", "spring"),
    "circuits": ("motor", "battery", "wire", "switch"),
    "structure": ("brace", "plate", "wedge"),
}


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
        self.yaw = 0
        self.flipped = False
        self.confirmed = False
        self.load_cap = 0.0
        self.load_used = 0.0
        self.stroke = None  # {start: Vec3, kind: str}
        self.blueprints = {}  # zone.key -> list of part dicts
        self._flags = {}
        self.last_invention = None

    def kinds(self, flags):
        k = ["box", "bar", "ball", "plate", "wedge"]
        if flags.get("first_invention") or flags.get("starter"):
            k += ["piston", "motor", "brace"]
        # Starter XP bias: branch toys unlock on pick or after that trial
        if flags.get("starter") == "hydraulics" or flags.get("trial_hydraulics") or flags.get("unlock_spring"):
            if "spring" not in k:
                k.append("spring")
        if flags.get("starter") == "circuits" or flags.get("trial_circuits") or flags.get("unlock_circuit_kit"):
            for x in ("battery", "wire", "switch"):
                if x not in k:
                    k.append(x)
        return k

    def mats(self, flags):
        m = ["wood", "steel"]
        for x in ("sticky", "icy", "bouncy"):
            if flags.get(x):
                m.append(x)
        return m

    def enter(self, zone, flags):
        self.leave(keep_blueprints=True)
        self.zone = zone
        self._flags = flags
        self.active = True
        self.goal_done = False
        self.testing = False
        self.confirmed = False
        self._i = 0
        self.yaw = 0
        self.flipped = False
        self.stroke = None
        self.load_cap = 0.0
        self.load_used = 0.0
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
        elif zone.key == "lab":
            starter = flags.get("starter")
            prefer = STARTER_PARTS.get(starter, ("box",))[0]
            self.kind = prefer if prefer in k else k[0]
        elif self.kind not in k:
            self.kind = k[0]
        self.material = "wood"
        self._spawn_crate()
        # Reload last blueprint for this pad
        if zone.key in self.blueprints:
            self._load_blueprint(self.blueprints[zone.key])
            self.message = "Blueprint reloaded. C weld, T test."
        self._ghost()
        mouse.locked = False

    def leave(self, keep_blueprints=False):
        if self.active and self.parts and self.zone:
            self.blueprints[self.zone.key] = self._dump_blueprint()
        self.active = False
        self.testing = False
        self.stroke = None
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
        self.confirmed = False
        self._homes = []
        if not keep_blueprints:
            pass

    def _base_scale(self, kind):
        return {
            "box": (0.9, 0.9, 0.9),
            "bar": (2.2, 0.32, 0.32),
            "ball": (0.7, 0.7, 0.7),
            "plate": (1.8, 0.18, 1.2),
            "wedge": (1.2, 0.7, 0.9),
            "piston": (0.5, 1.1, 0.5),
            "spring": (0.55, 0.9, 0.55),
            "motor": (0.9, 0.45, 0.9),
            "brace": (5.6, 0.4, 0.4),
            "battery": (0.7, 0.55, 0.45),
            "wire": (1.6, 0.12, 0.12),
            "switch": (0.5, 0.35, 0.5),
        }[kind]

    def _scale(self, kind, stroke_len=None):
        sx, sy, sz = self._base_scale(kind)
        if kind == "bar" and stroke_len is not None:
            sx = stroke_len
        if self.flipped:
            sx, sy = sy, sx
        if self.yaw % 2:
            sx, sz = sz, sx
        return (sx, sy, sz)

    def _model(self, kind):
        if kind == "ball":
            return "sphere"
        return "cube"

    def _prep(self, e, kind, mat):
        e.kind = kind
        e.mat = mat
        e.vx = 0.0
        e.vy = 0.0
        e.vz = 0.0
        e._grounded = False
        e._h0 = e.scale_y
        e._y0 = e.y
        e._x0 = e.x
        e._z0 = e.z
        e._sx0 = e.scale_x
        e._sy0 = e.scale_y
        e._sz0 = e.scale_z
        e.origin_y = -0.5
        e.welded = False
        e._island_static = False

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
        col = MATERIALS.get(self.material, (120, 220, 180))
        rgb = col[:3] if isinstance(col, tuple) else (120, 220, 180)
        self.ghost = solid(
            (*rgb, 150),
            parent=self.root,
            model=self._model(self.kind),
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

    def _place_point(self, scale=None):
        z = self.zone
        p = mouse.world_point
        if p is None or not z or not z.contains(p.x, p.z):
            p = self._slot()
        sx, sy, sz = scale or self._scale(self.kind)
        y = self._floor_y(p.x)
        for part in self.parts:
            if abs(part.x - p.x) < (part.scale_x + sx) * 0.45 and abs(part.z - p.z) < (part.scale_z + sz) * 0.45:
                y = max(y, sim.top_y(part))
        return Vec3(p.x, y, p.z if hasattr(p, "z") else z.z)

    def _mix_at(self, pos, scale):
        """If sticky ghost sits on wood/steel, return cladding material."""
        if self.material not in ("sticky", "wood", "steel"):
            return self.material
        for part in self.parts:
            if abs(part.x - pos.x) < (part.scale_x + scale[0]) * 0.5 and abs(part.z - pos.z) < (
                part.scale_z + scale[2]
            ) * 0.5:
                if abs(sim.top_y(part) - pos.y) < 0.2:
                    mixed = sim.mix_mat(self.material, part.mat)
                    if mixed:
                        return mixed
        return self.material

    def update(self):
        if not self.active:
            return
        dt = min(0.05, time.dt)
        if self.testing:
            self._step_test(dt)
            return
        if self.ghost:
            self.ghost.enabled = True
            if self.stroke and self.kind == "bar":
                cur = mouse.world_point or self.stroke["start"]
                length = max(1.2, min(5.8, abs(cur.x - self.stroke["start"].x) * 2 + 1.2))
                self.ghost.scale = self._scale("bar", stroke_len=length)
                mid = (self.stroke["start"] + Vec3(cur.x, self.stroke["start"].y, cur.z)) * 0.5
                mid.y = self.stroke["start"].y
                self.ghost.position = mid
            else:
                self.ghost.position = self._place_point()
                self.ghost.scale = self._scale(self.kind)

    def begin_stroke(self):
        if not self.active or self.testing:
            return
        if self.kind != "bar":
            self.place()
            return
        pos = self._place_point()
        self.stroke = {"start": Vec3(pos.x, pos.y, pos.z)}
        self.message = "Drag to draw a beam, release to place."

    def end_stroke(self):
        if not self.active or self.testing:
            return
        if not self.stroke:
            return
        start = self.stroke["start"]
        cur = mouse.world_point or start
        length = max(1.2, min(5.8, abs(cur.x - start.x) * 2 + abs(cur.z - start.z) * 2))
        if length < 1.35 and abs(cur.x - start.x) < 0.2 and abs(cur.z - start.z) < 0.2:
            # click without drag — default bar
            length = None
            pos = start
        else:
            mid_x = (start.x + cur.x) * 0.5
            mid_z = (start.z + cur.z) * 0.5
            pos = Vec3(mid_x, start.y, mid_z)
            # yaw toward drag
            if abs(cur.x - start.x) < abs(cur.z - start.z):
                self.yaw = 1
            else:
                self.yaw = 0
        self.stroke = None
        self._spawn_part(pos, "bar", length)

    def place(self):
        if not self.active or self.testing:
            return
        if self.kind == "bar":
            # click-place without stroke (Tab placed bars etc.)
            pos = self._place_point()
            self._spawn_part(pos, "bar", None)
            return
        scale = self._scale(self.kind)
        pos = self._place_point(scale)
        self._spawn_part(pos, self.kind, None)

    def _spawn_part(self, pos, kind, stroke_len):
        scale = self._scale(kind, stroke_len=stroke_len)
        mat = self._mix_at(pos, scale)
        p = solid(
            MATERIALS.get(mat, MATERIALS.get(self.material, (180, 180, 180))),
            parent=self.root,
            model=self._model(kind),
            position=pos,
            scale=scale,
            collider="box",
            origin_y=-0.5,
        )
        self._prep(p, kind, mat)
        self.parts.append(p)
        self._i += 1
        self.confirmed = False
        self.goal_done = False
        note = f" ({mat})" if mat != self.material else ""
        self.message = f"Placed {kind}{note}. C weld, T test."

    def rotate(self):
        if not self.active or self.testing:
            return
        self.yaw = (self.yaw + 1) % 4
        self.message = f"Rotate {self.yaw * 90}."

    def flip(self):
        if not self.active or self.testing:
            return
        self.flipped = not self.flipped
        self.message = "Flip to the axis R cannot reach."

    def cycle(self, flags):
        k = self.kinds(flags)
        i = k.index(self.kind) if self.kind in k else 0
        self.kind = k[(i + 1) % len(k)]
        self.yaw = 0
        self.flipped = False
        self.stroke = None
        self._ghost()

    def reset(self, flags):
        if not self.active or not self.zone:
            return
        zone = self.zone
        # clear blueprint for fresh pad
        self.blueprints.pop(zone.key, None)
        self.enter(zone, flags)
        self.message = "Pad reset."

    def set_mat(self, name, flags):
        if name in self.mats(flags):
            self.material = name
            self._ghost()

    def confirm(self):
        """Weld touching sticky/confirmed parts into islands (bible Confirm step)."""
        if not self.active or self.testing:
            return
        if not self.parts:
            self.message = "Place parts before welding."
            return
        sim.confirm_welds(self.parts, FLOOR)
        self.confirmed = True
        n = sum(1 for p in self.parts if p.welded)
        self.message = f"Welded {n} parts. T to test under gravity."

    def test(self):
        if not self.active:
            return
        if not self.parts:
            self.message = "Place at least one part first."
            return
        if not self.confirmed:
            # auto-confirm sticky touches so first-time players aren't stuck
            sim.confirm_welds(self.parts, FLOOR)
            self.confirmed = True
        self._restore()
        bias = self._flags.get("starter") == "structure"
        # Break weak spans before the run
        broken = sim.break_weak_spans(self.parts, self.zone.gap if self.zone else None, bias)
        for p in broken:
            self.parts.remove(p)
            destroy(p)
        if broken:
            self.message = f"{len(broken)} part(s) snapped — too weak for the span."
        self.testing = True
        self.test_t = 0.0
        self.goal_done = False
        self.load_cap = sim.load_capacity(self.parts, bias)
        self.load_used = 0.0
        if self.ghost:
            self.ghost.enabled = False
        for p in self.parts:
            p._y0 = p.y
            p._x0 = p.x
            p._z0 = p.z
            p._h0 = p.scale_y
            p._sx0 = p.scale_x
            p._sy0 = p.scale_y
            p._sz0 = p.scale_z
            p.vx = p.vy = p.vz = 0
            if abs(p.y - FLOOR) < 0.08:
                p._grounded = True
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
            if hasattr(p, "_sx0"):
                p.scale_x = p._sx0
                p.scale_z = p._sz0
            if hasattr(p, "_y0"):
                p.y = p._y0
                p.x = p._x0
                p.z = p._z0
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
        if self.crate:
            self.load_used = sim.props(self.crate)["mass"]
        if self.test_t >= TEST_TIME:
            self._finish_test()

    def _physics_step(self, dt):
        t = self.test_t
        # Refresh island static flags from weld graph each step
        static = [p for p in self.parts if not sim.is_dynamic(p)]
        dyn = [e for e in list(self.parts) + ([self.crate] if self.crate else []) if sim.is_dynamic(e)]

        powered = sim.circuit_powered(self.parts)

        for p in self.parts:
            if p.kind == "piston":
                grow = min(1.0, t / 0.7) * 1.5
                p.scale_y = p._h0 + grow
            if p.kind == "spring":
                # compress then kick upward
                phase = min(1.0, t / 0.5)
                if phase < 0.45:
                    p.scale_y = p._h0 * (1.0 - 0.35 * (phase / 0.45))
                else:
                    kick = min(1.0, (phase - 0.45) / 0.55)
                    p.scale_y = p._h0 * (0.65 + 0.9 * kick)
            if p.kind == "motor":
                if powered or not any(x.kind == "battery" for x in self.parts):
                    # legacy: motor alone still works if no battery on pad (workshop-era)
                    # circuit pad requires power
                    allow = powered or self.zone.goal != "roll" or not any(
                        x.kind in ("battery", "wire", "switch") for x in self.parts
                    )
                    # After circuit kit exists, roll goal needs power
                    if self.zone.goal == "roll" and any(x.kind == "battery" for x in self.parts):
                        allow = powered
                    elif self.zone.goal == "roll" and self._flags.get("trial_circuits"):
                        allow = powered or not self._flags.get("starter")
                    # simplify: if battery present, need power; else motor free
                    if any(x.kind == "battery" for x in self.parts):
                        allow = powered
                    else:
                        allow = True
                    if allow:
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
                bounce = sim.props(e)["bounce"]
                if bounce > 0.3 and e.vy < -1:
                    e.vy = -e.vy * bounce
                else:
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
            if p.kind in ("piston", "spring") and self.crate and sim.xz_overlap(p, self.crate, pad=0.05):
                if self.crate.y < sim.top_y(p) + 0.05:
                    sim.set_bottom(self.crate, sim.top_y(p))
                    if self.crate.vy < 0:
                        self.crate.vy = max(self.crate.vy, 0)
                    if p.kind == "spring" and t > 0.5:
                        self.crate.vy += 18.0 * dt
                    self.crate._grounded = True

        for d in dyn:
            for s in static:
                sim.separate(d, s)
            for other in dyn:
                if other is d:
                    continue
                sim.separate(d, other)

    def _finish_test(self):
        self.testing = False
        z = self.zone
        crate = self.crate
        ok = False
        bias = self._flags.get("starter") == "structure"
        self.load_cap = sim.load_capacity(self.parts, bias)
        self.load_used = sim.props(crate)["mass"] if crate else 0
        if not crate:
            ok = len(self.parts) > 0
        elif z.goal == "shelf":
            ok = crate.y > 1.05 and crate._grounded and self.load_cap >= self.load_used * 0.85
        elif z.goal == "lift":
            has_lift = any(p.kind in ("piston", "spring") for p in self.parts)
            ok = crate.y > z.lift_y - 0.15 and has_lift
        elif z.goal == "roll":
            start = z.x - z.w * 0.32
            has_motor = any(p.kind == "motor" for p in self.parts)
            needs_circuit = any(p.kind == "battery" for p in self.parts) or self._flags.get("starter") == "circuits"
            powered = (not needs_circuit) or sim.circuit_powered(self.parts)
            # After player has circuit kit (trial or starter), require the chain
            if self._flags.get("trial_circuits") or self._flags.get("starter") == "circuits":
                powered = sim.circuit_powered(self.parts)
                ok = crate.x > start + 2.2 and has_motor and powered
            else:
                ok = crate.x > start + 2.2 and has_motor
        elif z.goal == "span" and z.gap:
            ok = crate.x > z.gap[1] - 0.15 and crate.y > 0.15
        elif z.goal == "free":
            ok = crate.y > 0.2 and self.has_starter_part()
        else:
            ok = crate.y > 0.2
        self.goal_done = ok
        if ok:
            load_note = ""
            if z.goal == "shelf":
                load_note = f" Load {self.load_used:.1f}/{self.load_cap:.1f}."
            self.message = f"It holds!{load_note} Enter to stamp."
        else:
            if z.goal == "free" and not self.has_starter_part():
                self.message = "Capstone needs a starter part in the build."
            elif z.goal == "shelf" and crate and crate.y > 1.05 and self.load_cap < self.load_used * 0.85:
                self.message = f"Too weak — load {self.load_used:.1f}/{self.load_cap:.1f}. Add plate/brace."
            elif z.goal == "roll" and (self._flags.get("trial_circuits") or self._flags.get("starter") == "circuits"):
                self.message = "Need battery → wire/switch → motor. Rebuild."
            else:
                self.message = "Didn't hold — rebuild, C weld, T again."
        if self.ghost:
            self.ghost.enabled = True

    def has_starter_part(self):
        starter = self._flags.get("starter")
        need = STARTER_PARTS.get(starter)
        if not need:
            return True
        return any(p.kind in need for p in self.parts)

    def invention_name(self):
        z = self.zone.key if self.zone else "pad"
        starter = self._flags.get("starter") or "base"
        kinds = sorted({p.kind for p in self.parts})
        tip = kinds[0] if kinds else "thing"
        labels = {
            "workshop": "Shelf",
            "hydro": "Lift",
            "circuit": "Roller",
            "struct": "Span",
            "lab": "Capstone",
            "ravine": "Bridge",
            "shade": "Shade",
            "pylon": "Pylon",
            "storm": "Door",
        }
        return f"{labels.get(z, z.title())} · {tip} ({starter})"

    def _dump_blueprint(self):
        out = []
        for p in self.parts:
            out.append(
                {
                    "kind": p.kind,
                    "mat": p.mat,
                    "x": p.x,
                    "y": p.y,
                    "z": p.z,
                    "sx": p.scale_x,
                    "sy": p.scale_y,
                    "sz": p.scale_z,
                }
            )
        return out

    def _load_blueprint(self, data):
        for row in data:
            p = solid(
                MATERIALS.get(row["mat"], (180, 180, 180)),
                parent=self.root,
                model=self._model(row["kind"]),
                position=Vec3(row["x"], row["y"], row["z"]),
                scale=(row["sx"], row["sy"], row["sz"]),
                collider="box",
                origin_y=-0.5,
            )
            self._prep(p, row["kind"], row["mat"])
            self.parts.append(p)

    def delete_last(self):
        if self.testing:
            return
        if self.parts:
            destroy(self.parts.pop())
            self.message = "Removed last part."
            self.goal_done = False
            self.confirmed = False
