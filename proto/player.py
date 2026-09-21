"""Walker. Faces the way they walk; camera is a separate god-view."""

from __future__ import annotations

import math

from ursina import Entity, Vec3, held_keys, mouse, time

from proto.config import ACCENT, MOVE_SPEED, PEACH
from proto.figure import attach


class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Entity(
            parent=self,
            model="cube",
            position=(0, 0.85, 0),
            scale=(0.5, 1.7, 0.4),
            collider="box",
            visible=False,
        )
        attach(
            self,
            shirt=(244, 236, 220),
            pants=(86, 138, 196),
            hair=(92, 64, 52),
            accent=ACCENT,
            skin=PEACH,
            shoes=(72, 56, 48),
            look=4,
        )
        self.speed = MOVE_SPEED
        self.enabled_control = False
        self.rotation_y = 90
        self.cam = None
        mouse.locked = False

    def facing(self):
        ry = math.radians(self.rotation_y)
        return Vec3(math.sin(ry), 0, math.cos(ry))

    def strafe(self):
        f = self.facing()
        return Vec3(f.z, 0, -f.x)

    def enable(self):
        self.enabled_control = True

    def disable(self):
        self.enabled_control = False

    def teleport(self, x, z=0, y=0):
        self.position = Vec3(x, y, z)
        self.snap_camera()

    def snap_camera(self):
        if self.cam:
            self.cam.pull_to_player(snap=True)

    def input(self, key):
        return

    def update(self):
        if not self.enabled_control:
            return
        if self.cam and self.cam.overview:
            return
        if self.cam:
            fwd = self.cam.view_forward()
            right = self.cam.view_right()
        else:
            fwd = self.facing()
            right = self.strafe()
        move = fwd * (held_keys["w"] - held_keys["s"]) + right * (held_keys["d"] - held_keys["a"])
        move.y = 0
        if move.length() > 0:
            move = move.normalized()
            self.rotation_y = math.degrees(math.atan2(move.x, move.z))
            self.position += move * time.dt * self.speed
        self.y = 0
