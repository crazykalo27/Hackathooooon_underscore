"""God-view camera: play follow up close, free map past the zoom glide."""

from __future__ import annotations

import math

from ursina import Entity, Vec2, Vec3, Vec4, camera, held_keys, mouse, scene, time

from proto.config import (
    CAM_DIST,
    CAM_DIST_MAX,
    CAM_DIST_MIN,
    CAM_FOV,
    CAM_LOOK_Y,
    CAM_MAP_MIN,
    CAM_PITCH,
    CAM_PITCH_MAX,
    CAM_PITCH_MIN,
    CAM_PLAY_MAX,
    CAM_YAW,
)

# Seconds to ease across the play↔map dead band.
_GLIDE_SEC = 0.7


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
        self._glide = None
        player.cam = self
        camera.parent = scene
        camera.fov = CAM_FOV
        self._apply()

    @property
    def overview(self):
        """True once past play zoom — includes the glide into map."""
        return self.dist > CAM_PLAY_MAX + 0.5

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
        if self.overview:
            self._enter_play(snap=True, instant=True)
        else:
            self.pull_to_player(snap=True)

    def pin(self, x, z):
        """Hold look on a pad; same orbit/zoom/cutaway as play."""
        self.active = True
        self.frozen = False
        self.pinned = True
        self.allow_left_orbit = False
        if self.overview:
            self._enter_play(snap=False, instant=True)
        self.look = Vec3(x, CAM_LOOK_Y, z)
        self._apply()

    def pull_to_player(self, snap=False):
        if self.overview and not snap:
            return
        target = Vec3(self.player.x, CAM_LOOK_Y, self.player.z)
        if snap:
            self.look = target
        else:
            self.look = Vec3(target.x, CAM_LOOK_Y, target.z)
        self._apply()

    def _enter_map(self, instant=False):
        self._zoom = CAM_MAP_MIN
        self.pinned = False
        self.allow_left_orbit = True
        if instant:
            self.dist = CAM_MAP_MIN
            self._glide = None
        else:
            self._glide = CAM_MAP_MIN

    def _enter_play(self, snap=True, instant=False):
        self._zoom = CAM_PLAY_MAX
        if instant:
            self.dist = CAM_PLAY_MAX
            self._glide = None
        else:
            self._glide = CAM_PLAY_MAX
        if snap:
            self.look = Vec3(self.player.x, CAM_LOOK_Y, self.player.z)

    def input(self, key):
        if not self.active or self.frozen:
            return
        if key == "scroll left":
            self.yaw -= 8
            self._apply()
            return
        if key == "scroll right":
            self.yaw += 8
            self._apply()
            return

        out = key == "scroll down"
        inn = key == "scroll up"
        if not out and not inn:
            return

        # Already easing across the band — let scroll reverse the glide.
        if self._glide is not None:
            if out and self._glide == CAM_PLAY_MAX:
                self._enter_map()
            elif inn and self._glide == CAM_MAP_MIN:
                self._enter_play(snap=True)
            return

        step = max(2.2, self._zoom * 0.14)
        before = self._zoom
        if out:
            self._zoom += step
        else:
            self._zoom -= step
        self._zoom = max(CAM_DIST_MIN, min(CAM_DIST_MAX, self._zoom))

        # Crossing 35↔50% starts an auto zoom to the other side.
        if before <= CAM_PLAY_MAX and self._zoom > CAM_PLAY_MAX:
            self._enter_map()
        elif before >= CAM_MAP_MIN and self._zoom < CAM_MAP_MIN:
            self._enter_play(snap=True)
        self._apply()

    def update(self):
        if not self.active:
            return
        dt = time.dt if time.dt > 0 else 0.016
        if not self.frozen:
            self._orbit()
            self._arrows(dt)
            if self.overview and not self.pinned:
                self._wasd_pan(dt)
            self._zoom_step(dt)
            if not self.pinned and not self.overview:
                self.look = Vec3(self.player.x, CAM_LOOK_Y, self.player.z)
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
        if self.pinned and not self.overview:
            self.yaw += dx * 78 * dt
            self.pitch += dy * 58 * dt
            self.pitch = max(CAM_PITCH_MIN, min(CAM_PITCH_MAX, self.pitch))
            return
        speed = max(10.0, self.dist * 0.7)
        self.look += self.view_right() * dx * speed * dt
        self.look += self.view_forward() * dy * speed * dt
        self.look.y = CAM_LOOK_Y

    def _wasd_pan(self, dt):
        dx = held_keys["d"] - held_keys["a"]
        dy = held_keys["w"] - held_keys["s"]
        if dx == 0 and dy == 0:
            return
        speed = max(14.0, self.dist * 0.85)
        self.look += self.view_right() * dx * speed * dt
        self.look += self.view_forward() * dy * speed * dt
        self.look.y = CAM_LOOK_Y

    def _zoom_step(self, dt):
        if self._glide is not None:
            target = self._glide
            span = max(1.0, CAM_MAP_MIN - CAM_PLAY_MAX)
            rate = span / _GLIDE_SEC
            delta = target - self.dist
            step = rate * dt
            if abs(delta) <= step:
                self.dist = target
                self._zoom = target
                self._glide = None
            else:
                self.dist += math.copysign(step, delta)
                self._zoom = self.dist
            return

        self._zoom = max(CAM_DIST_MIN, min(CAM_DIST_MAX, self._zoom))
        if CAM_PLAY_MAX < self._zoom < CAM_MAP_MIN:
            self._zoom = CAM_MAP_MIN if self.dist >= (CAM_PLAY_MAX + CAM_MAP_MIN) * 0.5 else CAM_PLAY_MAX
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
        """Screen position for name tags, in UI space."""
        p3d = camera.getRelativePoint(scene, world_pos)
        full = camera.lens.getProjectionMat().xform(Vec4(p3d[0], p3d[1], p3d[2], 1.0))
        w = full[3]
        if w <= 0.08:
            return None
        aspect = float(camera.aspect_ratio or 1.6)
        return Vec2(full[0] / w * aspect, full[1] / w)

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
