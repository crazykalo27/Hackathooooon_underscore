"""Third-person walker. Blocky figure, camera follows."""

from __future__ import annotations

import math

from ursina import Entity, Vec3, camera, held_keys, mouse, scene, time

from proto.config import ACCENT, CREAM, HALL_HALF, MOVE_SPEED, PEACH
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
        attach(self, shirt=CREAM, pants=(92, 98, 118), hair=(72, 58, 68), accent=ACCENT, skin=PEACH)
        self.speed = MOVE_SPEED
        self.enabled_control = False
        self.rotation_y = 90
        mouse.locked = False
        camera.parent = scene
        camera.fov = 65
        self.snap_camera()

    def facing(self):
        ry = math.radians(self.rotation_y)
        return Vec3(math.sin(ry), 0, math.cos(ry))

    def strafe(self):
        f = self.facing()
        return Vec3(f.z, 0, -f.x)

    def enable(self):
        self.enabled_control = True
        mouse.locked = True

    def disable(self):
        self.enabled_control = False
        mouse.locked = False

    def teleport(self, x, z=0, y=0):
        self.position = Vec3(x, y, z)
        self.snap_camera()

    def _cam_target(self):
        f = self.facing()
        s = self.strafe()
        pos = self.world_position + Vec3(0, 3.1, 0) - f * 5.2 + s * 1.4
        pos.x = max(-2.0, pos.x)
        pos.z = max(-(HALL_HALF - 1.0), min(HALL_HALF - 1.0, pos.z))
        pos.y = 3.1
        return pos

    def _aim_camera(self, look_point):
        offset = look_point - camera.world_position
        ground = math.sqrt(offset.x * offset.x + offset.z * offset.z)
        camera.rotation_x = -math.degrees(math.atan2(offset.y, max(ground, 0.05)))
        camera.rotation_y = math.degrees(math.atan2(offset.x, offset.z))
        camera.rotation_z = 0

    def snap_camera(self):
        camera.parent = scene
        camera.position = self._cam_target()
        self._aim_camera(self.world_position + Vec3(0, 1.2, 0))

    def input(self, key):
        return

    def update(self):
        if not self.enabled_control:
            return
        self.rotation_y += mouse.velocity[0] * 45
        move = self.facing() * (held_keys["w"] - held_keys["s"]) + self.strafe() * (
            held_keys["d"] - held_keys["a"]
        )
        move.y = 0
        if move.length() > 0:
            self.position += move.normalized() * time.dt * self.speed
        self.y = 0
        self._follow_cam()

    def _follow_cam(self):
        target = self._cam_target()
        t = min(1, time.dt * 8) if time.dt > 0 else 1
        camera.position = Vec3(
            camera.x + (target.x - camera.x) * t,
            camera.y + (target.y - camera.y) * t,
            camera.z + (target.z - camera.z) * t,
        )
        self._aim_camera(self.world_position + Vec3(0, 1.15, 0))
