"""Title, HUD, dialogue, and a brass-framed iron build overlay."""

from __future__ import annotations

import time as wall

from ursina import Entity, Text, camera, window

from proto import story
from proto.config import (
    ACCENT,
    BRASS,
    BRASS_D,
    FONT,
    GOLD,
    IRON,
    IRON_B,
    LAMP,
    MATERIALS,
    MUTED,
    PAPER,
    PATINA,
    SHADOW,
    rgb,
)

WELL = (28, 22, 18)
PIP_OFF = (86, 72, 60)
CREAM_UI = PAPER
_SHARP = False


def _half_w():
    return max(0.72, window.aspect_ratio * 0.5)


def _sharpen(text_entity):
    global _SHARP
    font = getattr(text_entity, "_font", None)
    if font is None:
        return
    try:
        from panda3d.core import Texture

        nearest = getattr(Texture, "FT_nearest", None) or getattr(Texture, "FTNearest")
        font.setMagfilter(nearest)
        font.setMinfilter(nearest)
        font.setPixelsPerUnit(16)
        _SHARP = True
    except Exception:
        pass


def _quad(col, **kw):
    from proto.visuals import COLOR

    kw.setdefault("parent", camera.ui)
    kw.setdefault("model", "quad")
    kw["shader"] = COLOR
    kw["color"] = rgb(col) if isinstance(col, tuple) else col
    return Entity(**kw)


def _ink(text, x, y, scale=0.85, col=CREAM_UI, origin=(-0.5, 0.5), parent=None, **kw):
    kw.setdefault("parent", parent or camera.ui)
    t = Text(
        font=FONT,
        use_tags=False,
        text=_safe(text) or " ",
        x=x,
        y=y,
        origin=origin,
        scale=scale,
        color=rgb(col),
        line_height=0.95,
        **kw,
    )
    if not _SHARP:
        _sharpen(t)
    return t


def _safe(text):
    raw = text or ""
    return raw.replace("·", "*").replace("—", "-").replace("–", "-").replace("█", "#")


def _wrap(text, width):
    text = _safe(text).replace("\n", " ").strip()
    if width <= 0 or len(text) <= width:
        return text
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else f"{cur} {word}"
        if len(trial) > width:
            if cur:
                lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return "\n".join(lines)


def _fit(text, width, max_lines=2):
    lines = _wrap(text, width).split("\n")
    if len(lines) <= max_lines:
        return "\n".join(lines)
    last = lines[max_lines - 1][: max(1, width - 2)].rstrip() + ".."
    return "\n".join(lines[: max_lines - 1] + [last])


def _lift(col, k=40):
    return tuple(max(0, min(255, c + k)) for c in col[:3])


def _enable(items, on):
    for e in items:
        if e:
            e.enabled = on


def _pixel_frame(items, x, y, w, h, pips=True):
    """Iron plate, brass rivets and L-corners — same language as the hull."""
    items.append(_quad(SHADOW, scale=(w + 0.018, h + 0.018), x=x, y=y, z=2))
    items.append(_quad(IRON, scale=(w, h), x=x, y=y, z=1.6))
    items.append(_quad(WELL, scale=(w - 0.024, h - 0.024), x=x, y=y, z=1.4))
    items.append(_quad(BRASS, scale=(w - 0.042, 0.007), x=x, y=y + h * 0.5 - 0.026, z=1.2))
    items.append(_quad(BRASS_D, scale=(w - 0.042, 0.004), x=x, y=y - h * 0.5 + 0.020, z=1.2))
    hw, hh = w * 0.5, h * 0.5
    for sx, sy in ((-1, 1), (1, 1), (-1, -1), (1, -1)):
        cx, cy = x + sx * (hw - 0.012), y + sy * (hh - 0.012)
        items.append(_quad(BRASS, scale=(0.030, 0.007), x=cx - sx * 0.008, y=cy, z=1.1))
        items.append(_quad(BRASS, scale=(0.007, 0.030), x=cx, y=cy - sy * 0.008, z=1.1))
        items.append(_quad(GOLD, scale=(0.009, 0.009), x=cx, y=cy, z=1.0))
    if pips:
        top = y + hh - 0.038
        n = max(4, min(9, int(w / 0.046)))
        span = min(w * 0.62, 0.026 * n)
        x0 = x - span * 0.5
        step = span / max(1, n - 1)
        for i in range(n):
            col = LAMP if i % 3 == 0 else (BRASS if i % 2 == 0 else PIP_OFF)
            items.append(_quad(col, scale=(0.008, 0.008), x=x0 + i * step, y=top, z=1.0))
    top_in = 0.050 if pips else 0.034
    return (
        x - w * 0.5 + 0.032,
        x + w * 0.5 - 0.032,
        y + h * 0.5 - top_in,
        y - h * 0.5 + 0.032,
    )


def _bevel_btn(col, x, y, w, h, action, value, items):
    row = _quad(col, scale=(w, h), x=x, y=y, z=0.8, collider="box")
    row.action = action
    row.value = value
    items.append(row)
    items.append(_quad(_lift(col, 28), scale=(w * 0.88, 0.005), x=x, y=y + h * 0.5 - 0.006, z=0.6))
    items.append(_quad((18, 14, 12), scale=(w * 0.88, 0.004), x=x, y=y - h * 0.5 + 0.005, z=0.6))
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
        _enable(self.items, False)
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
        sig = (kinds, mats, builder.kind, builder.material, builder.goal_done, builder.zone.key if builder.zone else "")
        if sig == self._sig and self.enabled:
            if self.status:
                self.status.text = _fit(builder.message, 22, 2)
            if self._led:
                on = int(wall.time() * 2.4) % 2 == 0
                self._led.color = rgb(LAMP if on else PIP_OFF)
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

        kind_rows = max(1, (len(kinds) + 1) // 2)
        mat_rows = max(1, (len(mats) + 1) // 2)
        h = min(0.82, 0.44 + (kind_rows + mat_rows) * 0.048)
        w = 0.36
        x = _half_w() - w * 0.5 - 0.02
        y = 0.01
        left, right, top, bottom = _pixel_frame(self.items, x, y, w, h)

        self.items.append(_ink("SEEDED  BUILD", left, top, 0.92, LAMP))
        led_y = top - 0.008
        self._led = _quad(LAMP, scale=(0.012, 0.012), x=right - 0.048, y=led_y, z=0.5)
        self.items.append(self._led)
        self.items.append(_quad(PATINA, scale=(0.012, 0.012), x=right - 0.028, y=led_y, z=0.5))
        self.items.append(_quad(BRASS, scale=(0.012, 0.012), x=right - 0.008, y=led_y, z=0.5))

        zone = (builder.zone.key if builder.zone else "bay").upper()
        yy = top - 0.030
        self.items.append(_ink(f"BAY  ·  {zone}", left, yy, 0.78, PATINA))

        inner = right - left
        gap = 0.010
        cw = (inner - gap) * 0.5
        ch = 0.038
        xs = (left + cw * 0.5, left + cw + gap + cw * 0.5)

        yy -= 0.028
        self.items.append(_quad(BRASS, scale=(0.010, 0.010), x=left + 0.005, y=yy - 0.006, z=0.5))
        self.items.append(_ink("PART", left + 0.018, yy, 0.72, MUTED))
        yy -= 0.018 + ch * 0.5
        for i, kind in enumerate(kinds):
            on = kind == builder.kind
            bx = xs[i % 2]
            by = yy - (i // 2) * (ch + 0.008)
            _bevel_btn(ACCENT if on else IRON_B, bx, by, cw, ch, "kind", kind, self.items)
            self.items.append(
                _ink(kind.upper(), bx - cw * 0.5 + 0.012, by, 0.72, CREAM_UI if on else (210, 190, 168), origin=(-0.5, 0))
            )
        yy = yy - (kind_rows - 1) * (ch + 0.008) - ch * 0.5 - 0.016

        self.items.append(_quad(GOLD, scale=(0.010, 0.010), x=left + 0.005, y=yy - 0.006, z=0.5))
        self.items.append(_ink("MAT", left + 0.018, yy, 0.72, MUTED))
        yy -= 0.018 + ch * 0.5
        for i, mat in enumerate(mats):
            on = mat == builder.material
            bx = xs[i % 2]
            by = yy - (i // 2) * (ch + 0.008)
            swatch = MATERIALS.get(mat, MUTED)
            _bevel_btn(IRON_B if not on else _lift(swatch, -30), bx, by, cw, ch, "mat", mat, self.items)
            self.items.append(_quad(swatch, scale=(0.016, 0.022), x=bx - cw * 0.5 + 0.016, y=by, z=0.4))
            self.items.append(
                _ink(f"{i + 1} {mat.upper()}", bx - cw * 0.5 + 0.030, by, 0.7, CREAM_UI, origin=(-0.5, 0))
            )
        yy = yy - (mat_rows - 1) * (ch + 0.008) - ch * 0.5 - 0.014

        act_h = 0.040
        for action, caption, col in (("test", "T  TEST", PATINA), ("undo", "RMB  UNDO", (90, 78, 70))):
            _bevel_btn(col, x, yy, inner, act_h, action, action, self.items)
            self.items.append(_ink(caption, x, yy, 0.78, CREAM_UI, origin=(0, 0)))
            yy -= act_h + 0.010

        ready = builder.goal_done
        stamp = "ENTER  STAMP" if ready else "CLICK TO PLACE"
        self.items.append(_ink(stamp, x, bottom + 0.048, 0.78, GOLD if ready else CREAM_UI, origin=(0, 0.5)))
        self.status = _ink(_fit(builder.message, 22, 2), x, bottom + 0.008, 0.68, MUTED, origin=(0, 0.5))
        self.enabled = True
        _enable(self.items, True)
        self.status.enabled = True


class UI:
    def __init__(self):
        self.title = None
        self.hud_obj = None
        self.hud_meta = None
        self.hud_chrome = []
        self.banner = None
        self.banner_chrome = []
        self.prompt = None
        self.prompt_chrome = []
        self.talk_sp = None
        self.talk_tx = None
        self.talk_hint = None
        self.talk_chrome = []
        self.build_bar = None
        self.build_menu = BuildMenu()
        self.help = None
        self._build()

    def _build(self):
        hw = _half_w()
        hud_w, hud_h = 0.52, 0.192
        hud_x = -hw + hud_w * 0.5 + 0.026
        hud_y = 0.5 - hud_h * 0.5 - 0.016
        self._hud_box = _pixel_frame(self.hud_chrome, hud_x, hud_y, hud_w, hud_h)
        left, right, top, _bottom = self._hud_box
        self.hud_meta = _ink("", left, top, 0.88, LAMP)
        self.hud_obj = _ink("", left, top - 0.032, 0.84, CREAM_UI)
        self._hud = self.hud_chrome + [self.hud_meta, self.hud_obj]

        ban_h = 0.114
        ban_y = hud_y - hud_h * 0.5 - ban_h * 0.5 - 0.012
        self._ban_box = _pixel_frame(self.banner_chrome, hud_x, ban_y, hud_w, ban_h, pips=False)
        bl, _br, bt, _bb = self._ban_box
        self.banner = _ink("", bl, bt - 0.004, 0.8, LAMP)
        _enable(self.banner_chrome + [self.banner], False)

        talk_w = min(1.20, hw * 2 - 0.10)
        talk_h = 0.228
        talk_y = -0.5 + talk_h * 0.5 + 0.022
        self._talk_box = _pixel_frame(self.talk_chrome, 0, talk_y, talk_w, talk_h)
        tl, tr, tt, tb = self._talk_box
        self.talk_sp = _ink("", tl, tt, 0.95, LAMP)
        self.talk_tx = _ink("", tl, tt - 0.034, 0.88, CREAM_UI)
        self.talk_hint = _ink("E  CONTINUE", tr, tb + 0.004, 0.68, MUTED, origin=(0.5, 0))
        self._talk = self.talk_chrome + [self.talk_sp, self.talk_tx, self.talk_hint]
        _enable(self._talk, False)

        prompt_w, prompt_h = 0.64, 0.096
        prompt_y = -0.5 + prompt_h * 0.5 + 0.028
        self._prompt_box = _pixel_frame(self.prompt_chrome, 0, prompt_y, prompt_w, prompt_h, pips=False)
        pl, _pr, pt, _pb = self._prompt_box
        self.prompt = _ink("", 0, pt - 0.018, 0.92, LAMP, origin=(0, 0.5))
        self._prompt = self.prompt_chrome + [self.prompt]
        _enable(self._prompt, False)

        self.build_bar = None
        self.title_bits = []
        _tl, _tr, tt, _tb = _pixel_frame(self.title_bits, 0, 0.34, 0.70, 0.22)
        self.title_bits.append(_ink("SEEDED PROGRAM", 0, tt - 0.004, 0.78, LAMP, origin=(0, 0.5)))
        self.title_bits.append(_ink("UNDERSCORE", 0, tt - 0.064, 1.18, CREAM_UI, origin=(0, 0.5)))
        self.title_bits.append(_ink("ENTER TO WAKE", 0, tt - 0.122, 0.8, MUTED, origin=(0, 0.5)))

    def show_title(self, on):
        _enable(self.title_bits, on)
        _enable(self._hud, not on)
        if on:
            _enable(self._prompt, False)
            _enable(self.banner_chrome + [self.banner], False)
            _enable(self._talk, False)
            self.build_menu.hide()

    def refresh(self, state, near_npc=None, near_zone=None, dialogue=None, d_i=0, typed=0, builder=None):
        if state.mode == "title":
            self.show_title(True)
            return
        self.show_title(False)
        loc = {"ship": "SHIP · ACADEMY", "earth": "EARTH · C1", "c2": "EARTH · C2"}.get(state.map_name, state.map_name)
        hour = 6 + int((state.day_clock / 90) * 16)
        self.hud_meta.text = _safe(f"{loc}   DAY {state.day}  {hour:02d}h   {state.money()}c")
        self.hud_obj.text = _fit(story.objective(state.flags), 32, 2)

        show_banner = state.banner_t > 0 and state.banner and state.mode != "talk"
        _enable(self.banner_chrome + [self.banner], show_banner)
        if show_banner:
            self.banner.text = _fit(state.banner, 34, 2)

        talking = state.mode == "talk" and dialogue and d_i < len(dialogue)
        if talking:
            _enable(self._talk, True)
            _enable(self._prompt, False)
            sp, tx = dialogue[d_i]
            self.talk_sp.text = _safe(sp.upper())
            shown = tx[: int(typed)]
            body = _wrap(shown, 52)
            if int(typed) < len(tx) and int(wall.time() * 2.6) % 2 == 0:
                body += "#"
            self.talk_tx.text = body or " "
        else:
            _enable(self._talk, False)
            if state.mode == "play" and near_npc:
                _enable(self._prompt, True)
                self.prompt.text = _safe(f"E  TALK  *  {near_npc.npc_name.upper()}")
            elif state.mode == "play" and near_zone:
                _enable(self._prompt, True)
                self.prompt.text = _safe(f"B  BUILD  *  {near_zone.key.upper()}")
            else:
                _enable(self._prompt, False)

        if state.mode == "build" and builder:
            self.build_menu.present(builder, state.flags)
        else:
            self.build_menu.hide()

    def toggle_help(self):
        if self.help and self.help.enabled:
            self.help.enabled = False
            return
        if not self.help:
            self.help = Entity(parent=camera.ui)
            bits = []
            left, right, top, _bottom = _pixel_frame(bits, 0, 0, 0.64, 0.36)
            for e in bits:
                e.parent = self.help
            lines = (
                "WASD walk · drag orbit · scroll zoom",
                "E talk · B build on a glowing pad",
                "Build: A/D orbit · W/S zoom · scroll tilt",
                "T test · Enter stamp · RMB undo",
            )
            y = top - 0.008
            for line in lines:
                _ink(line, 0, y, 0.82, CREAM_UI, origin=(0, 0.5), parent=self.help)
                y -= 0.055
        self.help.enabled = True
