"""Startup loader so the window is not a frozen blank while the academy builds."""

from __future__ import annotations

import math

from ursina import Entity, Text, camera, destroy, time
from ursina import color as ursina_color

from proto.config import ACCENT, FONT, GOLD, IRON, LAMP, MUTED, PAPER, PATINA, SHADOW, SKY, rgb
from proto.visuals import COLOR


class LoadingScreen:
    def __init__(self):
        self.root = Entity(parent=camera.ui)
        self.t = 0.0
        self.fade = 1.0
        self.closing = False
        self.veil = Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(SKY),
            scale=3,
            z=2,
        )
        Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(SHADOW),
            scale=(0.60, 0.46),
            y=0.04,
            z=1.2,
        )
        Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(IRON),
            scale=(0.56, 0.42),
            y=0.04,
            z=1,
        )
        Text(
            parent=self.root,
            font=FONT,
            use_tags=False,
            text="SEEDED PROGRAM",
            y=0.18,
            origin=(0, 0),
            scale=0.78,
            color=rgb(LAMP),
        )
        Text(
            parent=self.root,
            font=FONT,
            use_tags=False,
            text="UNDERSCORE",
            y=0.10,
            origin=(0, 0),
            scale=1.2,
            color=rgb(PAPER),
        )
        self.status = Text(
            parent=self.root,
            font=FONT,
            use_tags=False,
            text="LOADING",
            y=-0.14,
            origin=(0, 0),
            scale=0.85,
            color=rgb(MUTED),
        )
        self.bar_bg = Entity(parent=self.root, model="quad", shader=COLOR, color=rgb(SHADOW), scale=(0.36, 0.02), y=-0.2, z=1)
        self.bar = Entity(parent=self.root, model="quad", shader=COLOR, color=rgb(LAMP), scale=(0.02, 0.02), y=-0.2, x=-0.17, z=0)
        self.cubes = []
        palette = (ACCENT, GOLD, PATINA, LAMP)
        for i, col in enumerate(palette):
            q = Entity(
                parent=self.root,
                model="quad",
                shader=COLOR,
                color=rgb(col),
                scale=0.045,
                x=-0.09 + i * 0.06,
                y=-0.02,
                z=0,
            )
            self.cubes.append(q)

    def set_status(self, text):
        self.status.text = text.upper()

    def set_progress(self, t):
        t = max(0.0, min(1.0, t))
        self.bar.scale_x = 0.02 + 0.34 * t
        self.bar.x = -0.17 + self.bar.scale_x * 0.5

    def tick(self, dt):
        self.t += dt
        dots = "." * (1 + int(self.t * 3) % 3)
        if not self.closing and self.status.text.startswith("LOAD"):
            self.status.text = "LOADING" + dots
        for i, q in enumerate(self.cubes):
            q.y = -0.02 + math.sin(self.t * 5 + i * 0.9) * 0.035
            q.rotation_z = self.t * 70 + i * 20
        if self.closing:
            self.fade = max(0.0, self.fade - dt * 2.8)
            a = int(self.fade * 255)
            self.veil.color = ursina_color.rgba(SKY[0], SKY[1], SKY[2], a)
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
    """Pumps a loader for a few frames, then builds the game in slices."""

    def __init__(self):
        super().__init__()
        self.screen = LoadingScreen()
        self.phase = 0
        self.wait = 0.0
        self.game = None

    def update(self):
        dt = time.dt
        alive = self.screen.tick(dt)
        if not alive:
            destroy(self)
            return
        if self.phase == 0:
            self.wait += dt
            self.screen.set_progress(0.12)
            if self.wait >= 0.18:
                self.screen.set_status("academy")
                self.phase = 1
        elif self.phase == 1:
            from proto.game import Game

            self.game = Game(autoload=False)
            self.screen.set_status("hall")
            self.screen.set_progress(0.4)
            self.phase = 2
        elif self.phase == 2:
            self.game.boot_world()
            self.screen.set_status("people")
            self.screen.set_progress(0.72)
            self.phase = 3
        elif self.phase == 3:
            self.game.boot_player()
            self.screen.set_progress(1)
            self.screen.dismiss()
            self.phase = 4
