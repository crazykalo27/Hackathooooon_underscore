"""Startup loader so the window is not a frozen blank while the academy builds."""

from __future__ import annotations

import math

from ursina import Entity, Text, camera, destroy, time
from ursina import color as ursina_color

from proto.config import ACCENT, FONT, GOLD, IRON, LAMP, MUTED, PAPER, PATINA, SHADOW, SPACE, rgb
from proto.visuals import COLOR


class LoadingScreen:
    def __init__(self):
        self.root = Entity(parent=camera.ui, z=-5)
        self.t = 0.0
        self.fade = 1.0
        self.closing = False
        self.veil = Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(SPACE),
            scale=4,
            z=2,
        )
        Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(SHADOW),
            scale=(0.72, 0.50),
            y=0.04,
            z=1.2,
        )
        Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(IRON),
            scale=(0.68, 0.46),
            y=0.04,
            z=1,
        )
        Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(LAMP),
            scale=(0.58, 0.008),
            y=0.22,
            z=0.5,
        )
        Text(
            parent=self.root,
            font=FONT,
            use_tags=False,
            text="SEEDED PROGRAM",
            y=0.16,
            origin=(0, 0),
            scale=1.0,
            color=rgb(LAMP),
        )
        Text(
            parent=self.root,
            font=FONT,
            use_tags=False,
            text="UNDERSCORE",
            y=0.07,
            origin=(0, 0),
            scale=1.5,
            color=rgb(PAPER),
        )
        self.status = Text(
            parent=self.root,
            font=FONT,
            use_tags=False,
            text="LOADING",
            y=-0.12,
            origin=(0, 0),
            scale=1.08,
            color=rgb(MUTED),
        )
        self.bar_bg = Entity(
            parent=self.root, model="quad", shader=COLOR, color=rgb(SHADOW), scale=(0.42, 0.024), y=-0.2, z=1
        )
        self.bar = Entity(
            parent=self.root, model="quad", shader=COLOR, color=rgb(LAMP), scale=(0.02, 0.024), y=-0.2, x=-0.2, z=0
        )
        self.cubes = []
        palette = (ACCENT, GOLD, PATINA, LAMP)
        for i, col in enumerate(palette):
            q = Entity(
                parent=self.root,
                model="quad",
                shader=COLOR,
                color=rgb(col),
                scale=0.05,
                x=-0.09 + i * 0.06,
                y=-0.02,
                z=0,
            )
            self.cubes.append(q)

    def set_status(self, text):
        self.status.text = (text or "LOADING").upper()

    def set_progress(self, t):
        t = max(0.0, min(1.0, t))
        self.bar.scale_x = 0.02 + 0.40 * t
        self.bar.x = -0.20 + self.bar.scale_x * 0.5

    def tick(self, dt):
        self.t += dt
        if not self.closing and self.status.text.startswith("LOAD"):
            self.status.text = "LOADING" + "." * (1 + int(self.t * 3) % 3)
        for i, q in enumerate(self.cubes):
            q.y = -0.02 + math.sin(self.t * 5 + i * 0.9) * 0.035
            q.rotation_z = self.t * 70 + i * 20
        if self.closing:
            self.fade = max(0.0, self.fade - dt * 1.8)
            a = int(self.fade * 255)
            self.veil.color = ursina_color.rgba(SPACE[0], SPACE[1], SPACE[2], a)
            if self.fade <= 0:
                destroy(self.root)
                return False
        return True

    def dismiss(self):
        self.closing = True
        self.set_status("ready")
        self.set_progress(1)
        for child in self.root.children:
            if child is not self.veil:
                child.enabled = False


class Boot(Entity):
    """Paints a real loader, then builds the academy one slice per frame."""

    def __init__(self):
        super().__init__()
        self.screen = LoadingScreen()
        self.phase = 0
        self.wait = 0.0
        self.game = None
        self.ready = False

    def update(self):
        dt = time.dt
        alive = self.screen.tick(dt)
        if not alive:
            destroy(self)
            return
        if self.phase == 0:
            self.wait += dt
            self.screen.set_status("LOADING")
            self.screen.set_progress(min(0.16, self.wait / 0.5 * 0.16))
            if self.wait >= 0.5:
                self.phase = 1
                self.ready = False
            return
        if self.phase == 1:
            if not self.ready:
                self.screen.set_status("SYSTEMS")
                self.screen.set_progress(0.18)
                self.ready = True
                return
            from proto.game import Game

            self.game = Game(autoload=False)
            self.phase = 2
            self.ready = False
            return
        if self.phase == 2:
            if not self.ready:
                self.screen.set_status("HULL")
                self.screen.set_progress(0.22)
                self.ready = True
                return
            self.game.world.begin_boot_load(self.game.state.flags)
            self.phase = 3
            self.ready = False
            return
        if self.phase == 3:
            nxt = self.game.world.peek_boot_load()
            if nxt is None:
                self.phase = 4
                self.ready = False
                return
            if not self.ready:
                self.screen.set_status(nxt)
                self.screen.set_progress(0.22 + 0.7 * self.game.world.load_frac)
                self.ready = True
                return
            more = self.game.world.step_boot_load()
            self.screen.set_progress(0.22 + 0.7 * self.game.world.load_frac)
            self.ready = False
            if not more:
                self.phase = 4
            return
        if self.phase == 4:
            if not self.ready:
                self.screen.set_status("READY")
                self.screen.set_progress(1)
                self.ready = True
                return
            self.game.boot_player()
            self.screen.dismiss()
            self.phase = 5
