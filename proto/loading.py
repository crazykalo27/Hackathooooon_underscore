"""Startup loader so the window is not a frozen blank while the academy builds."""

from __future__ import annotations

import math

from ursina import Entity, Text, camera, destroy, time
from ursina import color as ursina_color

from proto.config import (
    FONT,
    SKY,
    UI_CLAY,
    UI_CREAM,
    UI_CREAM_D,
    UI_GOLD,
    UI_GRASS,
    UI_INK,
    UI_MUTED,
    UI_ROOF,
    UI_SHADOW,
    rgb,
)
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
            color=rgb(SKY),
            scale=4,
            z=2,
        )
        Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(UI_SHADOW),
            scale=(0.62, 0.40),
            y=0.02,
            z=1.3,
        )
        Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(UI_CREAM),
            scale=(0.60, 0.38),
            y=0.03,
            z=1,
        )
        Entity(
            parent=self.root,
            model="quad",
            shader=COLOR,
            color=rgb(UI_CREAM_D),
            scale=(0.60, 0.012),
            y=-0.154,
            z=0.8,
        )
        Text(
            parent=self.root,
            font=FONT,
            use_tags=False,
            text="Underscore",
            y=0.12,
            origin=(0, 0),
            scale=1.45,
            color=rgb(UI_INK),
        )
        Text(
            parent=self.root,
            font=FONT,
            use_tags=False,
            text="setting the table",
            y=0.04,
            origin=(0, 0),
            scale=0.95,
            color=rgb(UI_MUTED),
        )
        self.status = Text(
            parent=self.root,
            font=FONT,
            use_tags=False,
            text="loading",
            y=-0.10,
            origin=(0, 0),
            scale=0.95,
            color=rgb(UI_MUTED),
        )
        self.bar_bg = Entity(
            parent=self.root, model="quad", shader=COLOR, color=rgb(UI_CREAM_D), scale=(0.40, 0.016), y=-0.16, z=1
        )
        self.bar = Entity(
            parent=self.root, model="quad", shader=COLOR, color=rgb(UI_ROOF), scale=(0.02, 0.016), y=-0.16, x=-0.19, z=0
        )
        self.cubes = []
        palette = (UI_GRASS, UI_GOLD, UI_ROOF, UI_CLAY)
        for i, col in enumerate(palette):
            q = Entity(
                parent=self.root,
                model="circle" if i % 2 else "quad",
                shader=COLOR,
                color=rgb(col),
                scale=0.036,
                x=-0.08 + i * 0.054,
                y=-0.02,
                z=0,
            )
            self.cubes.append(q)

    def set_status(self, text):
        raw = (text or "loading").replace("_", " ").strip().lower()
        self.status.text = raw

    def set_progress(self, t):
        t = max(0.0, min(1.0, t))
        self.bar.scale_x = 0.02 + 0.38 * t
        self.bar.x = -0.19 + self.bar.scale_x * 0.5

    def tick(self, dt):
        self.t += dt
        if not self.closing and self.status.text.startswith("load"):
            self.status.text = "loading" + "." * (1 + int(self.t * 3) % 3)
        for i, q in enumerate(self.cubes):
            q.y = -0.02 + math.sin(self.t * 5 + i * 0.9) * 0.028
            q.rotation_z = self.t * 50 + i * 20
        if self.closing:
            self.fade = max(0.0, self.fade - dt * 1.8)
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
            self.screen.set_status("loading")
            self.screen.set_progress(min(0.16, self.wait / 0.5 * 0.16))
            if self.wait >= 0.5:
                self.phase = 1
                self.ready = False
            return
        if self.phase == 1:
            if not self.ready:
                self.screen.set_status("waking")
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
                self.screen.set_status("the hall")
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
                self.screen.set_status("ready")
                self.screen.set_progress(1)
                self.ready = True
                return
            self.game.boot_player()
            self.screen.dismiss()
            self.phase = 5
