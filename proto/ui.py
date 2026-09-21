"""Title, HUD, dialogue, and a Pocket Build-style toy overlay."""

from __future__ import annotations

import time as wall

from ursina import Entity, Text, camera, window

from proto import story
from proto.config import (
    FONT,
    MATERIALS,
    STARTERS,
    UI_CHIP,
    UI_CHIP_DEEP,
    UI_CLAY,
    UI_CREAM,
    UI_CREAM_D,
    UI_GOLD,
    UI_GRASS,
    UI_INK,
    UI_MUTED,
    UI_PEACH,
    UI_ROOF,
    UI_SHADOW,
    UI_WOOD,
    rgb,
)

_SHARP = False

KIND_GLYPH = {
    "box": (UI_WOOD, (0.030, 0.030)),
    "bar": (UI_ROOF, (0.044, 0.012)),
    "ball": (UI_CLAY, (0.028, 0.028)),
    "plate": (UI_PEACH, (0.040, 0.016)),
    "wedge": (UI_CLAY, (0.032, 0.022)),
    "piston": (UI_GRASS, (0.016, 0.036)),
    "spring": (UI_GOLD, (0.018, 0.032)),
    "motor": (UI_GOLD, (0.028, 0.028)),
    "brace": (UI_PEACH, (0.036, 0.016)),
    "battery": (UI_GRASS, (0.024, 0.020)),
    "wire": (UI_ROOF, (0.040, 0.008)),
    "switch": (UI_CLAY, (0.022, 0.022)),
}

NODE_LABELS = {
    "first_invention": "Base kit",
    "trial_hydraulics": "Hydraulics trial",
    "trial_circuits": "Circuits trial",
    "trial_structure": "Structure trial",
    "capstone": "Capstone",
    "sticky": "Sticky",
    "icy": "Icy",
    "bouncy": "Bouncy",
    "registered": "Registered",
}

PICK_BLURBS = {
    "hydraulics": "Pistons and springs. Weight and lift.",
    "circuits": "Battery, wire, switch, motor.",
    "structure": "Plates, braces, stronger spans.",
}

WORLDS = {"ship": "Academy", "earth": "Colony 1", "c2": "Colony 2"}


def _half_w():
    return max(0.72, window.aspect_ratio * 0.5)


def _sharpen(text_entity):
    global _SHARP
    font = getattr(text_entity, "_font", None)
    if font is None:
        return
    try:
        font.setPixelsPerUnit(72)
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


def _dot(col, x, y, s=0.018, z=0.5, parent=None):
    from proto.visuals import COLOR

    try:
        return Entity(
            parent=parent or camera.ui,
            model="circle",
            shader=COLOR,
            color=rgb(col) if isinstance(col, tuple) else col,
            scale=s,
            x=x,
            y=y,
            z=z,
        )
    except Exception:
        return _quad(col, parent=parent or camera.ui, scale=(s, s), x=x, y=y, z=z)


def _ink(text, x, y, scale=1.05, col=UI_INK, origin=(-0.5, 0.5), parent=None, **kw):
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
        line_height=1.12,
        **kw,
    )
    if not _SHARP:
        _sharpen(t)
    return t


def _safe(text):
    raw = text or ""
    return raw.replace("·", "*").replace("—", "-").replace("–", "-").replace("█", "#")


def _pretty(text):
    return _safe(text).replace("_", " ").strip()


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


def _enable(items, on):
    for e in items:
        if e:
            e.enabled = on


def _inset(x, y, w, h, pad=0.028, top_extra=0.0):
    return (
        x - w * 0.5 + pad,
        x + w * 0.5 - pad,
        y + h * 0.5 - pad - top_extra,
        y - h * 0.5 + pad,
    )


def _chip(items, x, y, w, h):
    """Slim navy bar — Pocket Build's top status strip."""
    items.append(_quad(UI_SHADOW, scale=(w + 0.012, h + 0.012), x=x, y=y - 0.005, z=2))
    items.append(_quad(UI_CHIP, scale=(w, h), x=x, y=y, z=1.6))
    items.append(_quad(UI_CHIP_DEEP, scale=(w, 0.006), x=x, y=y - h * 0.5 + 0.003, z=1.4))
    return _inset(x, y, w, h, pad=0.024)


def _card(items, x, y, w, h):
    """Cream toy card: lid + darker underside, like a cake-slice tile."""
    items.append(_quad(UI_SHADOW, scale=(w + 0.018, h + 0.018), x=x, y=y - 0.008, z=2))
    items.append(_quad(UI_CREAM, scale=(w, h), x=x, y=y, z=1.6))
    items.append(_quad(UI_CREAM_D, scale=(w, 0.010), x=x, y=y - h * 0.5 + 0.005, z=1.4))
    return _inset(x, y, w, h, pad=0.026)


def _keycap(items, x, y, letter, parent=None):
    cap = _quad(UI_CREAM, scale=(0.036, 0.032), x=x, y=y, z=0.6)
    if parent:
        cap.parent = parent
    items.append(cap)
    items.append(_ink(letter, x, y + 0.002, 0.78, UI_INK, origin=(0, 0), parent=parent))
    return cap


def _hit(col, x, y, w, h, action, value, items, z=0.8):
    row = _quad(col, scale=(w, h), x=x, y=y, z=z, collider="box")
    row.action = action
    row.value = value
    items.append(row)
    return row


class BuildMenu:
    def __init__(self):
        self.items = []
        self.status = None
        self._sig = None
        self.enabled = False

    def hide(self):
        self.enabled = False
        self._sig = None
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
                builder.yaw = 0
                builder.flipped = False
                builder._ghost()
                return True
            if action == "mat":
                builder.set_mat(e.value, flags)
                return True
            if action == "weld":
                builder.confirm()
                return True
            if action == "test":
                builder.test()
                return True
            if action == "undo":
                builder.delete_last()
                return True
            if action == "reset":
                builder.reset(flags)
                return True
        return False

    def present(self, builder, flags):
        kinds = tuple(builder.kinds(flags))
        mats = tuple(builder.mats(flags))
        load = (round(builder.load_cap, 1), round(builder.load_used, 1), builder.confirmed)
        sig = (
            kinds,
            mats,
            builder.kind,
            builder.material,
            builder.goal_done,
            builder.zone.key if builder.zone else "",
            load,
        )
        if sig == self._sig and self.enabled:
            if self.status:
                self.status.text = _fit(builder.message, 22, 2)
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

        cols = 3
        kind_rows = max(1, (len(kinds) + cols - 1) // cols)
        tile = 0.072
        gap = 0.008
        inner_w = cols * tile + (cols - 1) * gap
        w = inner_w + 0.064
        h = 0.36 + kind_rows * (tile + 0.020) + 0.24
        h = min(0.96, h)
        x = _half_w() - w * 0.5 - 0.028
        y = -0.02
        left, right, top, bottom = _card(self.items, x, y, w, h)

        self.items.append(_ink("Build", left, top, 1.18, UI_INK))
        zone = _pretty(builder.zone.key if builder.zone else "pad")
        self.items.append(_ink(zone, right, top, 0.88, UI_MUTED, origin=(0.5, 0.5)))

        yy = top - 0.052
        xs0 = left + tile * 0.5
        for i, kind in enumerate(kinds):
            on = kind == builder.kind
            bx = xs0 + (i % cols) * (tile + gap)
            by = yy - (i // cols) * (tile + 0.020)
            if on:
                self.items.append(_quad(UI_ROOF, scale=(tile + 0.010, tile + 0.010), x=bx, y=by, z=0.85))
            _hit(UI_CREAM if on else UI_CREAM_D, bx, by, tile, tile, "kind", kind, self.items)
            gcol, gsz = KIND_GLYPH.get(kind, (UI_WOOD, (0.028, 0.028)))
            if kind in ("ball", "motor", "switch"):
                self.items.append(_dot(gcol, bx, by + 0.006, s=gsz[0], z=0.4))
            else:
                self.items.append(_quad(gcol, scale=gsz, x=bx, y=by + 0.006, z=0.4))
            self.items.append(_ink(_pretty(kind), bx, by - tile * 0.42, 0.58, UI_INK if on else UI_MUTED, origin=(0, 0.5)))

        yy = yy - kind_rows * (tile + 0.020) - 0.010
        self.items.append(_ink("Color", left, yy, 0.82, UI_MUTED))
        yy -= 0.036
        sw = 0.034
        for i, mat in enumerate(mats):
            on = mat == builder.material
            bx = left + 0.018 + i * (sw + 0.022)
            swatch = MATERIALS.get(mat, UI_MUTED)
            if on:
                self.items.append(_dot(UI_ROOF, bx, yy, s=sw + 0.014, z=0.55))
            _hit((0, 0, 0, 0), bx, yy, sw + 0.01, sw + 0.01, "mat", mat, self.items, z=0.5)
            self.items.append(_dot(swatch, bx, yy, s=sw, z=0.45))

        yy -= 0.044
        if builder.zone and builder.zone.goal == "shelf":
            self.items.append(
                _ink(
                    f"Load {builder.load_used:.1f} / {builder.load_cap:.1f}",
                    left,
                    yy,
                    0.78,
                    UI_ROOF if builder.load_cap >= builder.load_used * 0.85 else UI_CLAY,
                )
            )
            yy -= 0.028

        act_w = right - left
        act_h = 0.040
        weld_col = UI_ROOF if builder.confirmed else UI_GOLD
        for action, caption, fill, ink in (
            ("weld", "Weld  C", weld_col, UI_CREAM if builder.confirmed else UI_INK),
            ("test", "Test  T", UI_GRASS, UI_INK),
            ("undo", "Undo", UI_CREAM_D, UI_INK),
            ("reset", "Reset  X", UI_CLAY, UI_CREAM),
        ):
            _hit(fill, x, yy, act_w, act_h, action, action, self.items)
            self.items.append(_ink(caption, x, yy, 0.88, ink, origin=(0, 0)))
            yy -= act_h + 0.008

        ready = builder.goal_done
        stamp = "Enter to stamp" if ready else "Drag bar · click place"
        self.items.append(_ink("R spin   F flip", x, bottom + 0.052, 0.72, UI_MUTED, origin=(0, 0.5)))
        self.items.append(_ink(stamp, x, bottom + 0.028, 0.88, UI_ROOF if ready else UI_INK, origin=(0, 0.5)))
        self.status = _ink(_fit(builder.message, 22, 2), x, bottom + 0.004, 0.78, UI_MUTED, origin=(0, 0.5))
        self.enabled = True
        _enable(self.items, True)
        self.status.enabled = True


class UI:
    def __init__(self):
        self.title = None
        self.hud_obj = None
        self.hud_meta = None
        self.hud_day = None
        self.hud_coin = None
        self.hud_zoom = None
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
        self.name_slots = []
        self.pick_items = []
        self.pick_hits = []
        self.flash_items = []
        self.catalog_items = []
        self._flash_sig = None
        self._pick_sig = None
        self._catalog_sig = None
        self._build()

    def _build(self):
        hw = _half_w()
        bar_w = min(hw * 2 - 0.06, 1.72)
        bar_h = 0.074
        bar_y = 0.5 - bar_h * 0.5 - 0.016
        left, right, top, bottom = _chip(self.hud_chrome, 0, bar_y, bar_w, bar_h)
        mid_y = (top + bottom) * 0.5
        self.hud_chrome.append(_dot(UI_PEACH, left + 0.008, mid_y, s=0.022, z=0.5))
        self.hud_meta = _ink("", left + 0.028, mid_y + 0.002, 1.12, UI_CREAM, origin=(-0.5, 0))
        self.hud_zoom = _ink("", 0.02, mid_y + 0.002, 0.95, UI_CREAM, origin=(0, 0))
        self.hud_chrome.append(_dot(UI_GOLD, right - 0.168, mid_y, s=0.016, z=0.5))
        self.hud_coin = _ink("", right - 0.154, mid_y + 0.002, 0.95, UI_CREAM, origin=(-0.5, 0))
        self.hud_chrome.append(_dot(UI_GRASS, right - 0.078, mid_y, s=0.016, z=0.5))
        self.hud_day = _ink("", right - 0.064, mid_y + 0.002, 0.95, UI_CREAM, origin=(-0.5, 0))
        self.hud_chrome.append(_dot(UI_ROOF, right - 0.006, mid_y, s=0.020, z=0.5))
        self.hud_chrome.append(_ink("?", right - 0.006, mid_y + 0.002, 0.72, UI_CREAM, origin=(0, 0)))

        obj_w, obj_h = 0.50, 0.092
        obj_x = -hw + obj_w * 0.5 + 0.030
        obj_y = bar_y - bar_h * 0.5 - obj_h * 0.5 - 0.012
        ol, _or, ot, _ob = _card(self.hud_chrome, obj_x, obj_y, obj_w, obj_h)
        self.hud_obj = _ink("", ol, ot - 0.002, 0.98, UI_INK)
        self._hud = self.hud_chrome + [self.hud_meta, self.hud_obj, self.hud_day, self.hud_coin, self.hud_zoom]

        ban_w, ban_h = 0.56, 0.088
        ban_y = obj_y - obj_h * 0.5 - ban_h * 0.5 - 0.010
        bl, _br, bt, _bb = _card(self.banner_chrome, 0, ban_y, ban_w, ban_h)
        self.banner = _ink("", 0, (bt + _bb) * 0.5, 1.0, UI_INK, origin=(0, 0))
        _enable(self.banner_chrome + [self.banner], False)

        talk_w = min(1.16, hw * 2 - 0.12)
        talk_h = 0.22
        talk_y = -0.5 + talk_h * 0.5 + 0.028
        tl, tr, tt, tb = _card(self.talk_chrome, 0, talk_y, talk_w, talk_h)
        self.talk_sp = _ink("", tl, tt, 1.12, UI_ROOF)
        self.talk_tx = _ink("", tl, tt - 0.040, 1.05, UI_INK)
        self.talk_hint = _ink("E to continue", tr, tb + 0.002, 0.78, UI_MUTED, origin=(0.5, 0))
        self._talk = self.talk_chrome + [self.talk_sp, self.talk_tx, self.talk_hint]
        _enable(self._talk, False)

        prompt_w, prompt_h = 0.52, 0.072
        prompt_y = -0.5 + prompt_h * 0.5 + 0.030
        _chip(self.prompt_chrome, 0, prompt_y, prompt_w, prompt_h)
        self.prompt = _ink("", 0.018, prompt_y + 0.002, 1.0, UI_CREAM, origin=(0, 0))
        self._prompt = self.prompt_chrome + [self.prompt]
        _enable(self._prompt, False)

        self.build_bar = None
        self.title_bits = []
        self.title_bits.append(_dot(UI_GRASS, -0.08, 0.40, s=0.028, z=0.5))
        self.title_bits.append(_dot(UI_GOLD, -0.02, 0.418, s=0.018, z=0.5))
        self.title_bits.append(_dot(UI_ROOF, 0.04, 0.40, s=0.022, z=0.5))
        self.title_bits.append(_dot(UI_CLAY, 0.09, 0.412, s=0.014, z=0.5))
        self.title_bits.append(_ink("Underscore", 0, 0.30, 1.55, UI_CREAM, origin=(0, 0.5)))
        self.title_bits.append(_ink("a little world on a table", 0, 0.22, 1.0, UI_MUTED, origin=(0, 0.5)))
        _chip(self.title_bits, 0, 0.12, 0.28, 0.064)
        self.title_bits.append(_ink("Enter", 0, 0.122, 1.05, UI_CREAM, origin=(0, 0)))
        self.title_cont = _ink("C  continue", 0, 0.04, 0.88, UI_MUTED, origin=(0, 0.5))
        self.title_bits.append(self.title_cont)

    def show_title(self, on):
        from proto.state import State

        _enable(self.title_bits, on)
        if on:
            self.title_cont.enabled = State.has_save()
        _enable(self._hud, not on)
        if on:
            _enable(self._prompt, False)
            _enable(self.banner_chrome + [self.banner], False)
            _enable(self._talk, False)
            self.build_menu.hide()
            self._hide_pick()
            self._hide_flash()
            self._hide_catalog()
            self.sync_names([], None, False)

    def refresh(self, state, near_npc=None, near_zone=None, dialogue=None, d_i=0, typed=0, builder=None, zoom_pct=None):
        if state.mode == "title":
            self.show_title(True)
            return
        self.show_title(False)
        self.hud_meta.text = _pretty(WORLDS.get(state.map_name, state.map_name))
        self.hud_day.text = str(state.day)
        self.hud_coin.text = str(state.money())
        if zoom_pct is None:
            self.hud_zoom.text = ""
        else:
            self.hud_zoom.text = f"{int(round(zoom_pct))}%"
        self.hud_obj.text = _fit(story.objective(state.flags), 28, 2)

        show_banner = state.banner_t > 0 and state.banner and state.mode not in ("talk", "pick")
        _enable(self.banner_chrome + [self.banner], show_banner)
        if show_banner:
            self.banner.text = _fit(state.banner, 32, 2)

        if state.mode == "pick":
            self._present_pick(state)
            _enable(self._talk, False)
            _enable(self._prompt, False)
            self.build_menu.hide()
            self._hide_catalog()
        else:
            self._hide_pick()

        talking = state.mode == "talk" and dialogue and d_i < len(dialogue)
        if talking:
            _enable(self._talk, True)
            _enable(self._prompt, False)
            sp, tx = dialogue[d_i]
            self.talk_sp.text = _pretty(sp)
            shown = tx[: int(typed)]
            body = _wrap(shown, 46)
            if int(typed) < len(tx) and int(wall.time() * 2.6) % 2 == 0:
                body += "."
            self.talk_tx.text = body or " "
        elif state.mode != "pick":
            _enable(self._talk, False)
            if state.mode == "play" and near_npc:
                _enable(self._prompt, True)
                self.prompt.text = _safe(f"E   Talk to {near_npc.npc_name}")
            elif state.mode == "play" and near_zone:
                _enable(self._prompt, True)
                self.prompt.text = _safe(f"B   Build {_pretty(near_zone.key)}")
            else:
                _enable(self._prompt, False)

        if state.mode == "build" and builder:
            self.build_menu.present(builder, state.flags)
            self._present_catalog(state)
        else:
            self.build_menu.hide()
            if state.mode != "play":
                self._hide_catalog()
            else:
                self._present_catalog(state, compact=True)

        if state.flash_t > 0 and state.flash_node:
            self._present_flash(state)
        else:
            self._hide_flash()

    def _hide_pick(self):
        from ursina import destroy

        for e in self.pick_items:
            destroy(e)
        self.pick_items.clear()
        self.pick_hits.clear()
        self._pick_sig = None

    def _present_pick(self, state):
        sig = (state.pick_focus, tuple(STARTERS))
        if sig == self._pick_sig and self.pick_items:
            return
        self._hide_pick()
        self._pick_sig = sig
        left, right, top, bottom = _card(self.pick_items, 0, 0.02, 1.14, 0.52)
        self.pick_items.append(_ink("Pick a starter", 0, top - 0.01, 1.25, UI_INK, origin=(0, 0.5)))
        self.pick_items.append(
            _ink("Bias, not a prison. 1 / 2 / 3 or click.", 0, top - 0.055, 0.85, UI_MUTED, origin=(0, 0.5))
        )
        card_w = 0.32
        gap = 0.04
        total = 3 * card_w + 2 * gap
        x0 = -total * 0.5 + card_w * 0.5
        for i, branch in enumerate(STARTERS):
            on = i == state.pick_focus
            cx = x0 + i * (card_w + gap)
            cy = -0.02
            ch = 0.28
            if on:
                self.pick_items.append(_quad(UI_ROOF, scale=(card_w + 0.018, ch + 0.018), x=cx, y=cy, z=1.7))
            hit = _hit(UI_CREAM if on else UI_CREAM_D, cx, cy, card_w, ch, "pick", branch, self.pick_items, z=1.5)
            self.pick_hits.append(hit)
            self.pick_items.append(_ink(f"{i + 1}", cx, cy + 0.10, 0.9, UI_MUTED, origin=(0, 0.5)))
            self.pick_items.append(_ink(_pretty(branch), cx, cy + 0.04, 1.05, UI_INK, origin=(0, 0.5)))
            self.pick_items.append(
                _ink(_fit(PICK_BLURBS[branch], 16, 3), cx, cy - 0.04, 0.72, UI_MUTED, origin=(0, 0.5))
            )
        self.pick_items.append(_ink("Enter confirm · Esc cancel", 0, bottom + 0.02, 0.8, UI_MUTED, origin=(0, 0.5)))

    def pick_hit(self):
        for e in self.pick_hits:
            if getattr(e, "hovered", False) and getattr(e, "action", None) == "pick":
                return e.value
        return None

    def _hide_flash(self):
        from ursina import destroy

        for e in self.flash_items:
            destroy(e)
        self.flash_items.clear()
        self._flash_sig = None

    def _present_flash(self, state):
        node = state.flash_node
        sig = (node, int(state.flash_t * 2))
        if sig[0] == getattr(self, "_flash_node", None) and self.flash_items:
            return
        self._hide_flash()
        self._flash_node = node
        label = NODE_LABELS.get(node, _pretty(node.replace("starter:", "Starter · ")))
        if str(node).startswith("starter:"):
            label = f"Starter · {_pretty(str(node).split(':', 1)[1])}"
        hw = _half_w()
        x = hw - 0.28
        y = 0.18
        left, right, top, bottom = _card(self.flash_items, x, y, 0.42, 0.16)
        self.flash_items.append(_dot(UI_GOLD, left + 0.02, (top + bottom) * 0.5 + 0.02, s=0.028, z=0.4))
        self.flash_items.append(_ink("Catalog node", left + 0.05, top - 0.01, 0.78, UI_MUTED))
        self.flash_items.append(_ink(label, left + 0.05, top - 0.045, 1.1, UI_ROOF))
        self.flash_items.append(_ink("Knowledge unlocked", left + 0.05, bottom + 0.02, 0.72, UI_INK))

    def _hide_catalog(self):
        from ursina import destroy

        for e in self.catalog_items:
            destroy(e)
        self.catalog_items.clear()
        self._catalog_sig = None

    def _present_catalog(self, state, compact=False):
        inv = state.inventions()
        sig = (tuple(i["name"] for i in inv[-5:]), compact, state.mode)
        if sig == self._catalog_sig and self.catalog_items:
            return
        self._hide_catalog()
        if not inv:
            return
        self._catalog_sig = sig
        hw = _half_w()
        rows = inv[-4:] if compact else inv[-6:]
        h = 0.06 + len(rows) * 0.038
        w = 0.40
        x = -hw + w * 0.5 + 0.028
        y = -0.18 if not compact else -0.22
        left, _r, top, _b = _card(self.catalog_items, x, y, w, h)
        self.catalog_items.append(_ink("Inventions", left, top - 0.002, 0.85, UI_MUTED))
        yy = top - 0.032
        for row in reversed(rows):
            self.catalog_items.append(_ink(_fit(row["name"], 22, 1), left, yy, 0.72, UI_INK))
            yy -= 0.034

    def catalog_hit(self):
        return False

    def sync_names(self, npcs, cam, visible=True):
        from ursina import Vec3

        if not visible or cam is None:
            for slot in self.name_slots:
                slot["label"].enabled = False
            return
        while len(self.name_slots) < len(npcs):
            label = _ink(" ", 0, 0, 1.2, UI_CREAM, origin=(0, 0))
            label.z = 0.35
            self.name_slots.append({"label": label})
        for i, npc in enumerate(npcs):
            slot = self.name_slots[i]
            pos = npc.world_position
            head = Vec3(pos.x, pos.y + 1.95, pos.z)
            scr = cam._project(head)
            if scr is None:
                slot["label"].enabled = False
                continue
            name = _pretty(getattr(npc, "npc_name", "") or "")
            slot["label"].enabled = True
            slot["label"].text = name or " "
            slot["label"].x = scr.x
            slot["label"].y = scr.y + 0.045
        for j in range(len(npcs), len(self.name_slots)):
            self.name_slots[j]["label"].enabled = False

    def toggle_help(self):
        if self.help and self.help.enabled:
            self.help.enabled = False
            return
        if not self.help:
            self.help = Entity(parent=camera.ui)
            bits = []
            left, _right, top, _bottom = _card(bits, 0, 0, 0.78, 0.44)
            for e in bits:
                e.parent = self.help
            lines = (
                "WASD walk · arrows pan · drag orbit · scroll zoom",
                "E talk · B build · P starter pick",
                "Build: drag bar · C weld · T test · X reset",
                "Enter stamp · right click undo",
            )
            y = top - 0.004
            for line in lines:
                _ink(line, 0, y, 0.92, UI_INK, origin=(0, 0.5), parent=self.help)
                y -= 0.058
        self.help.enabled = True
