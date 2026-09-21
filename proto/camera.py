"""God-view camera: orbit/zoom freely, pan when the player nears the cutaway rim."""

from __future__ import annotations

import math

from ursina import Entity, Vec2, Vec3, Vec4, camera, held_keys, mouse, scene, time

from proto.config import (
    CAM_DIST,
    CAM_DIST_MAX,
    CAM_DIST_MIN,
    CAM_EDGE,
    CAM_FOV,
    CAM_LOOK_Y,
    CAM_PITCH,
    CAM_PITCH_MAX,
    CAM_PITCH_MIN,
    CAM_YAW,
)


class GodCam(Entity):
    def __init__(self, player, world):
        super().__init__()
        self.player = player
        self.world = world
        self.active = True
        self.frozen = False
        self.pinned = False
        self.allow_left_orbit = True
        self.look = Vec3(player.x, CAM_LOOK_Y, player.z)
        self.yaw = CAM_YAW
        self.pitch = CAM_PITCH
        self.dist = CAM_DIST
        self._zoom = CAM_DIST
        player.cam = self
        camera.parent = scene
        camera.fov = CAM_FOV
        self._apply()

    def view_forward(self):
        yaw = math.radians(self.yaw)
        return Vec3(math.sin(yaw), 0, math.cos(yaw))

    def view_right(self):
        f = self.view_forward()
        return Vec3(f.z, 0, -f.x)

    def pause(self):
        self.active = False
        self.world.set_hull_hidden(None)

    def resume(self):
        self.active = True
        self.frozen = False
        self.pinned = False
        self.allow_left_orbit = True
        self.pull_to_player(snap=True)

    def pin(self, x, z):
        """Hold look on a pad; same orbit/zoom/cutaway as play."""
        self.active = True
        self.frozen = False
        self.pinned = True
        self.allow_left_orbit = False
        self.look = Vec3(x, CAM_LOOK_Y, z)
        self._apply()

    def pull_to_player(self, snap=False):
        target = Vec3(self.player.x, CAM_LOOK_Y, self.player.z)
        if snap:
            self.look = target
        else:
            self.look = Vec3(
                self.look.x + (target.x - self.look.x),
                CAM_LOOK_Y,
                self.look.z + (target.z - self.look.z),
            )
        self._apply()

    def input(self, key):
        if not self.active or self.frozen:
            return
        step = max(2.2, self._zoom * 0.14)
        if key == "scroll up":
            self._zoom -= step
        elif key == "scroll down":
            self._zoom += step
        elif key == "scroll left":
            self.yaw -= 8
            self._apply()
        elif key == "scroll right":
            self.yaw += 8
            self._apply()
        self._zoom = max(CAM_DIST_MIN, min(CAM_DIST_MAX, self._zoom))

    def update(self):
        if not self.active:
            return
        dt = time.dt if time.dt > 0 else 0.016
        if not self.frozen:
            self._orbit()
            self._arrows(dt)
            self._zoom_step(dt)
        self._apply()
        if not self.frozen and not self.pinned:
            for _ in range(3):
                if not self._edge_follow(dt):
                    break
                self._apply()

    def _orbit(self):
        dragging = mouse.locked or mouse.right or mouse.middle
        if self.allow_left_orbit and mouse.left:
            dragging = True
        if not dragging:
            return
        vx, vy = mouse.velocity[0], mouse.velocity[1]
        if abs(vx) < 0.0001 and abs(vy) < 0.0001:
            return
        gain = 110 if mouse.locked else 95
        self.yaw += vx * gain
        self.pitch += vy * gain * 0.85
        self.pitch = max(CAM_PITCH_MIN, min(CAM_PITCH_MAX, self.pitch))

    def _arrows(self, dt):
        dx = held_keys["right arrow"] - held_keys["left arrow"]
        dy = held_keys["up arrow"] - held_keys["down arrow"]
        if dx == 0 and dy == 0:
            return
        if self.pinned:
            self.yaw += dx * 78 * dt
            self.pitch += dy * 58 * dt
            self.pitch = max(CAM_PITCH_MIN, min(CAM_PITCH_MAX, self.pitch))
            return
        speed = max(10.0, self.dist * 0.7)
        self.look += self.view_right() * dx * speed * dt
        self.look += self.view_forward() * dy * speed * dt
        self.look.y = CAM_LOOK_Y

    def _zoom_step(self, dt):
        self._zoom = max(CAM_DIST_MIN, min(CAM_DIST_MAX, self._zoom))
        k = min(1.0, dt * 10)
        self.dist += (self._zoom - self.dist) * k

    def _orbit_pos(self):
        pitch = math.radians(self.pitch)
        yaw = math.radians(self.yaw)
        cy = math.cos(pitch)
        ox = -math.sin(yaw) * cy * self.dist
        oy = math.sin(pitch) * self.dist
        oz = -math.cos(yaw) * cy * self.dist
        return self.look + Vec3(ox, oy, oz)

    def _project(self, world_pos):
        """Shader-space offset: (ndc.x * aspect, ndc.y), same as the hull hole."""
        p3d = camera.getRelativePoint(scene, world_pos)
        full = camera.lens.getProjectionMat().xform(Vec4(p3d[0], p3d[1], p3d[2], 1.0))
        w = full[3]
        if w <= 0.08:
            return None
        aspect = float(camera.aspect_ratio or 1.6)
        return Vec2(full[0] / w * aspect, full[1] / w)

    def _edge_follow(self, dt):
        from proto.world import cut_screen_radius

        hole = cut_screen_radius(self.dist)
        limit = hole * (1.0 - CAM_EDGE)
        head = Vec3(self.player.x, CAM_LOOK_Y, self.player.z)
        scr = self._project(head)
        if scr is None:
            self.look = head
            return True
        mag = math.sqrt(scr.x * scr.x + scr.y * scr.y)
        if mag <= limit + 0.002:
            return False
        extra = mag - limit
        half = math.tan(math.radians(max(camera.fov, 1.0)) * 0.5)
        world_per = self.dist * half
        right = Vec3(camera.right.x, 0, camera.right.z)
        if right.length() > 0.05:
            right = right.normalized()
        else:
            right = self.view_right()
        up = Vec3(camera.up.x, 0, camera.up.z)
        if up.length() < 0.08:
            up = Vec3(-camera.forward.x, 0, -camera.forward.z)
        if up.length() > 0.05:
            up = up.normalized()
        else:
            up = self.view_forward()
        inv = 1.0 / mag
        self.look += right * (scr.x * inv) * extra * world_per
        self.look += up * (scr.y * inv) * extra * world_per
        self.look.y = CAM_LOOK_Y
        return True

    def _apply(self):
        self.pitch = max(CAM_PITCH_MIN, min(CAM_PITCH_MAX, self.pitch))
        self.dist = max(CAM_DIST_MIN, min(CAM_DIST_MAX, self.dist))
        pos = self._orbit_pos()
        floor = self.player.y + 2.4
        if pos.y < floor:
            extra = math.degrees(math.asin(min(1.0, floor / max(self.dist, 0.2))))
            self.pitch = max(self.pitch, extra)
            pos = self._orbit_pos()
            pos.y = max(pos.y, floor)

        camera.parent = scene
        camera.position = pos
        offset = self.look - pos
        ground = math.sqrt(offset.x * offset.x + offset.z * offset.z)
        camera.rotation_x = -math.degrees(math.atan2(offset.y, max(ground, 0.05)))
        camera.rotation_y = math.degrees(math.atan2(offset.x, offset.z))
        camera.rotation_z = 0
        self.world.apply_cutaway(pos, self.look, self.dist)
