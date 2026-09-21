"""Title, HUD, dialogue, and a pixel space-age build overlay."""

from __future__ import annotations

import time as wall

from ursina import Entity, Text, camera, color

from proto import story
from proto.config import ACCENT, GOLD, INK, MATERIALS, MUTED, STAR, TEAL, rgb
from proto.visuals import COLOR

NAVY = (20, 24, 40)
PANEL = (32, 38, 58)
WELL = (14, 16, 30)
EDGE = (88, 196, 186)
PIP_OFF = (48, 56, 72)
CREAM_UI = (250, 242, 230)


def _quad(col, **kw):
    kw.setdefault("parent", camera.ui)
    kw.setdefault("model", "quad")
    kw["shader"] = COLOR
    kw["color"] = rgb(col) if isinstance(col, tuple) else col
    return Entity(**kw)


def _label(text, x, y, scale=0.65, col=CREAM_UI, **kw):
    kw.setdefault("origin", (0, 0))
    return Text(parent=camera.ui, text=text, x=x, y=y, scale=scale, color=rgb(col), **kw)


def _lift(col, k=40):
    return tuple(min(255, c + k) for c in col[:3])


def _pixel_frame(items, x, y, w, h):
    """Chunky hull plate with L-corners, screws, and a teal hairline."""
    items.append(_quad(NAVY, scale=(w + 0.016, h + 0.016), x=x, y=y, z=2))
    items.append(_quad(PANEL, scale=(w, h), x=x, y=y, z=1.6))
    items.append(_quad(WELL, scale=(w - 0.022, h - 0.022), x=x, y=y, z=1.4))
    items.append(_quad(EDGE, scale=(w - 0.04, 0.007), x=x, y=y + h * 0.5 - 0.028, z=1.2))
    items.append(_quad(EDGE, scale=(w - 0.04, 0.004), x=x, y=y - h * 0.5 + 0.022, z=1.2))
    hw, hh = w * 0.5, h * 0.5
    for sx, sy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        cx, cy = x + sx * (hw - 0.012), y + sy * (hh - 0.012)
        items.append(_quad(EDGE, scale=(0.032, 0.007), x=cx - sx * 0.008, y=cy, z=1.1))
        items.append(_quad(EDGE, scale=(0.007, 0.032), x=cx, y=cy - sy * 0.008, z=1.1))
        items.append(_quad(GOLD, scale=(0.01, 0.01), x=cx, y=cy, z=1.0))
    top = y + hh - 0.042
    for i in range(9):
        items.append(
            _quad(STAR if i % 3 == 0 else (90, 110, 130), scale=(0.008, 0.008), x=x - w * 0.32 + i * 0.026, y=top, z=1.0)
        )


def _bevel_btn(col, x, y, w, h, action, value, items):
    row = _quad(col, scale=(w, h), x=x, y=y, z=0.8, collider="box")
    row.action = action
    row.value = value
    items.append(row)
    items.append(_quad(_lift(col, 36), scale=(w * 0.9, 0.006), x=x, y=y + h * 0.5 - 0.007, z=0.6))
    items.append(_quad((12, 14, 22), scale=(w * 0.9, 0.004), x=x, y=y - h * 0.5 + 0.006, z=0.6))
    return row


class BuildMenu:
    def __init__(self):
        self.items = []
        self.status = None
        self._sig = None
        self._led = None
        self.enabled = False

    def hide(self):
        self.enabled = False
        self._sig = None
        self._led = None
        for e in self.items:
            e.enabled = False
        if self.status:
            self.status.enabled = False

    def consume_click(self, builder, flags):
        if not self.enabled:
            return False
        for e in self.items:
            if not getattr(e, "hovered", False):
                continue
            action = getattr(e, "action", None)
            if action == "kind":
                builder.kind = e.value
                builder._ghost()
                return True
            if action == "mat":
                builder.set_mat(e.value, flags)
                return True
            if action == "test":
                builder.test()
                return True
            if action == "undo":
                builder.delete_last()
                return True
        return False

    def present(self, builder, flags):
        kinds = tuple(builder.kinds(flags))
        mats = tuple(builder.mats(flags))
        sig = (kinds, mats, builder.kind, builder.material, builder.goal_done, builder.message, builder.zone.key if builder.zone else "")
        if sig == self._sig and self.enabled:
            if self.status:
                self.status.text = builder.message
            if self._led:
                on = int(wall.time() * 2.4) % 2 == 0
                self._led.color = rgb(TEAL if on else PIP_OFF)
            return
        self._sig = sig
        self._rebuild(builder, kinds, mats)

    def _rebuild(self, builder, kinds, mats):
        from ursina import destroy

        for e in self.items:
            destroy(e)
        self.items.clear()
        if self.status:
            destroy(self.status)
            self.status = None

        x, y = 0.39, 0.02
        w, h = 0.30, 0.84
        _pixel_frame(self.items, x, y, w, h)

        head = y + h * 0.5 - 0.07
        self.items.append(_label("SEEDED  //  BUILD", x, head, 0.62, ACCENT))
        self._led = _quad(TEAL, scale=(0.014, 0.014), x=x + 0.118, y=head, z=0.5)
        self.items.append(self._led)
        self.items.append(_quad(PIP_OFF, scale=(0.014, 0.014), x=x + 0.136, y=head, z=0.5))
        self.items.append(_quad(GOLD, scale=(0.014, 0.014), x=x + 0.154, y=head, z=0.5))

        zone = (builder.zone.key if builder.zone else "bay").upper()
        self.items.append(_label(f"BAY  ·  {zone}", x, head - 0.04, 0.58, TEAL))
        self.items.append(_label("PWR OK   COM 01   LINK", x, head - 0.068, 0.5, MUTED))

        yy = head - 0.11
        self.items.append(_quad(EDGE, scale=(0.012, 0.012), x=x - 0.11, y=yy, z=0.5))
        self.items.append(_label("PART", x - 0.02, yy, 0.58, MUTED))
        yy -= 0.048
        for kind in kinds:
            on = kind == builder.kind
            _bevel_btn(ACCENT if on else PANEL, x, yy, 0.22, 0.042, "kind", kind, self.items)
            self.items.append(_label(kind.upper(), x, yy, 0.62, CREAM_UI if on else (186, 196, 210)))
            yy -= 0.046

        yy -= 0.012
        self.items.append(_quad(GOLD, scale=(0.012, 0.012), x=x - 0.11, y=yy, z=0.5))
        self.items.append(_label("MAT", x - 0.028, yy, 0.58, MUTED))
        yy -= 0.048
        for i, mat in enumerate(mats):
            on = mat == builder.material
            swatch = MATERIALS.get(mat, MUTED)
            _bevel_btn(PANEL if not on else _lift(swatch, -20), x, yy, 0.22, 0.042, "mat", mat, self.items)
            self.items.append(_quad(swatch, scale=(0.02, 0.028), x=x - 0.086, y=yy, z=0.4))
            self.items.append(_label(f"{i + 1}  {mat.upper()}", x + 0.012, yy, 0.6, CREAM_UI))
            yy -= 0.046

        yy -= 0.01
        for action, caption, col in (
            ("test", "T   TEST", TEAL),
            ("undo", "RMB  UNDO", (96, 104, 124)),
        ):
            _bevel_btn(col, x, yy, 0.22, 0.044, action, action, self.items)
            self.items.append(_label(caption, x, yy, 0.62, CREAM_UI))
            yy -= 0.05

        ready = builder.goal_done
        stamp = "ENTER  STAMP" if ready else "CLICK TO PLACE"
        self.items.append(_label(stamp, x, y - h * 0.5 + 0.07, 0.62, GOLD if ready else CREAM_UI))
        self.status = Text(
            parent=camera.ui,
            text=builder.message,
            x=x,
            y=y - h * 0.5 + 0.038,
            origin=(0, 0),
            scale=0.52,
            color=rgb(MUTED),
            wordwrap=24,
        )
        self.enabled = True
        for e in self.items:
            e.enabled = True
        self.status.enabled = True


class UI:
    def __init__(self):
        self.title = None
        self.hud_obj = None
        self.hud_meta = None
        self.hud_chrome = []
        self.banner = None
        self.prompt = None
        self.talk_sp = None
        self.talk_tx = None
        self.talk_hint = None
        self.build_bar = None
        self.build_menu = BuildMenu()
        self.help = None
        self._build()

    def _build(self):
        self.hud_chrome = []
        _pixel_frame(self.hud_chrome, -0.48, 0.40, 0.62, 0.15)
        self.hud_meta = Text("", parent=camera.ui, position=(-0.74, 0.445), origin=(-0.5, 0.5), scale=0.85, color=rgb(ACCENT))
        self.hud_obj = Text("", parent=camera.ui, position=(-0.74, 0.392), origin=(-0.5, 0.5), scale=0.8, color=rgb(CREAM_UI), wordwrap=42)
        self.banner = Text("", parent=camera.ui, position=(0, 0.28), origin=(0, 0), scale=1.1, color=rgb(ACCENT), enabled=False)
        self.prompt = Text("", parent=camera.ui, position=(0, -0.42), origin=(0, 0), scale=1.15, color=rgb(TEAL), enabled=False)
        self.build_bar = Text("", parent=camera.ui, position=(0, -0.47), origin=(0, 0), scale=1.0, color=color.white, enabled=False)

        self.talk_sp = Text(parent=camera.ui, text="", y=-0.34, scale=1.0, color=rgb(ACCENT), origin=(0, 0), enabled=False)
        self.talk_tx = Text(parent=camera.ui, text="", y=-0.40, scale=0.9, color=rgb(CREAM_UI), origin=(0, 0), wordwrap=42, enabled=False)
        self.talk_hint = Text(parent=camera.ui, text="E / Enter  continue", y=-0.46, scale=0.75, color=rgb(MUTED), origin=(0, 0), enabled=False)

        self.title_bits = [
            Text(parent=camera.ui, text="SEEDED PROGRAM", y=0.42, scale=0.7, color=rgb(ACCENT), origin=(0, 0)),
            Text(parent=camera.ui, text="UNDERSCORE", y=0.36, scale=1.05, color=rgb(INK), origin=(0, 0)),
            Text(parent=camera.ui, text="ENTER to wake up", y=0.30, scale=0.75, color=rgb(INK), origin=(0, 0)),
        ]

    def show_title(self, on):
        for bit in self.title_bits:
            bit.enabled = on
        for e in self.hud_chrome:
            e.enabled = not on
        if on:
            self.hud_meta.enabled = False
            self.hud_obj.enabled = False
            self.prompt.enabled = False
            self.banner.enabled = False
            self.build_bar.enabled = False
            self.talk_sp.enabled = False
            self.talk_tx.enabled = False
            self.talk_hint.enabled = False
            self.build_menu.hide()

    def refresh(self, state, near_npc=None, near_zone=None, dialogue=None, d_i=0, typed=0, builder=None):
        if state.mode == "title":
            self.show_title(True)
            return
        self.show_title(False)
        self.hud_meta.enabled = True
        self.hud_obj.enabled = True
        loc = {"ship": "SHIP · ACADEMY", "earth": "EARTH · C1", "c2": "EARTH · C2"}.get(state.map_name, state.map_name)
        hour = 6 + int((state.day_clock / 90) * 16)
        self.hud_meta.text = f"{loc}   DAY {state.day}  {hour:02d}h   {state.money()}c"
        self.hud_obj.text = story.objective(state.flags)

        if state.banner_t > 0 and state.banner:
            self.banner.enabled = True
            self.banner.text = state.banner
        else:
            self.banner.enabled = False

        talking = state.mode == "talk" and dialogue and d_i < len(dialogue)
        if talking:
            self.talk_sp.enabled = True
            self.talk_tx.enabled = True
            self.talk_hint.enabled = True
            sp, tx = dialogue[d_i]
            self.talk_sp.text = sp.upper()
            self.talk_tx.text = tx[: int(typed)]
            self.prompt.enabled = False
        else:
            self.talk_sp.enabled = False
            self.talk_tx.enabled = False
            self.talk_hint.enabled = False
            if state.mode == "play" and near_npc:
                self.prompt.enabled = True
                self.prompt.text = f"E  talk to {near_npc.npc_name}"
            elif state.mode == "play" and near_zone:
                self.prompt.enabled = True
                self.prompt.text = f"B  build · {near_zone.key}"
            else:
                self.prompt.enabled = False

        if state.mode == "build" and builder:
            self.build_bar.enabled = False
            self.build_menu.present(builder, state.flags)
        else:
            self.build_bar.enabled = False
            self.build_menu.hide()

    def toggle_help(self):
        if self.help and self.help.enabled:
            self.help.enabled = False
            return
        if not self.help:
            self.help = Entity(parent=camera.ui)
            bits = []
            _pixel_frame(bits, 0, 0, 0.62, 0.34)
            for e in bits:
                e.parent = self.help
            lines = [
                "WASD walk · mouse look · Esc unlock mouse",
                "E talk · B build on a glowing pad",
                "Build: A/D orbit · W/S zoom · scroll tilt",
                "T test · Enter stamp · RMB undo",
            ]
            y = 0.1
            for line in lines:
                Text(parent=self.help, text=line, y=y, scale=0.85, color=rgb(CREAM_UI), origin=(0, 0))
                y -= 0.055
        self.help.enabled = True
