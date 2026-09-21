"""Title, HUD, dialogue, and the build tray."""

from __future__ import annotations

from ursina import Entity, Text, camera, color

from proto import story
from proto.config import ACCENT, CREAM, INK, MATERIALS, MUTED, PAPER, TEAL, rgb
from proto.visuals import COLOR


def _quad(col, **kw):
    kw.setdefault("parent", camera.ui)
    kw.setdefault("model", "quad")
    kw["shader"] = COLOR
    kw["color"] = rgb(col) if isinstance(col, tuple) else col
    return Entity(**kw)


class BuildMenu:
    def __init__(self):
        self.items = []
        self.status = None
        self._sig = None
        self.enabled = False

    def hide(self):
        self.enabled = False
        self._sig = None
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
            return
        self._sig = sig
        self._rebuild(builder, kinds, mats)

    def _rebuild(self, builder, kinds, mats):
        for e in self.items:
            from ursina import destroy

            destroy(e)
        self.items.clear()
        if self.status:
            from ursina import destroy

            destroy(self.status)
            self.status = None

        panel = _quad(PAPER, scale=(0.26, 0.78), x=0.38, y=0.0, z=1, collider=None)
        self.items.append(panel)
        title = Text(parent=camera.ui, text="BUILD", x=0.38, y=0.36, origin=(0, 0), scale=0.85, color=rgb(ACCENT))
        self.items.append(title)
        zone = builder.zone.key.upper() if builder.zone else ""
        sub = Text(parent=camera.ui, text=zone, x=0.38, y=0.31, origin=(0, 0), scale=0.7, color=rgb(INK))
        self.items.append(sub)

        y = 0.24
        hint = Text(parent=camera.ui, text="PART", x=0.38, y=y, origin=(0, 0), scale=0.65, color=rgb(MUTED))
        self.items.append(hint)
        y -= 0.055
        for kind in kinds:
            on = kind == builder.kind
            row = _quad(ACCENT if on else CREAM, scale=(0.2, 0.045), x=0.38, y=y, collider="box")
            row.action = "kind"
            row.value = kind
            label = Text(parent=camera.ui, text=kind, x=0.38, y=y, origin=(0, 0), scale=0.7, color=rgb(PAPER if on else INK))
            self.items.extend((row, label))
            y -= 0.05

        y -= 0.02
        hint = Text(parent=camera.ui, text="MATERIAL", x=0.38, y=y, origin=(0, 0), scale=0.65, color=rgb(MUTED))
        self.items.append(hint)
        y -= 0.055
        for i, mat in enumerate(mats):
            on = mat == builder.material
            swatch = MATERIALS.get(mat, MUTED)
            row = _quad(swatch if on else CREAM, scale=(0.2, 0.045), x=0.38, y=y, collider="box")
            row.action = "mat"
            row.value = mat
            label = Text(parent=camera.ui, text=f"{i+1}  {mat}", x=0.38, y=y, origin=(0, 0), scale=0.7, color=rgb(INK))
            self.items.extend((row, label))
            y -= 0.05

        y -= 0.02
        for action, caption, col in (
            ("test", "T  test", TEAL),
            ("undo", "RMB  undo", MUTED),
        ):
            row = _quad(col, scale=(0.2, 0.045), x=0.38, y=y, collider="box")
            row.action = action
            row.value = action
            label = Text(parent=camera.ui, text=caption, x=0.38, y=y, origin=(0, 0), scale=0.7, color=rgb(PAPER))
            self.items.extend((row, label))
            y -= 0.05

        stamp = "ENTER  stamp" if builder.goal_done else "click pad to place"
        foot = Text(parent=camera.ui, text=stamp, x=0.38, y=-0.36, origin=(0, 0), scale=0.7, color=rgb(ACCENT if builder.goal_done else INK))
        self.items.append(foot)
        self.status = Text(parent=camera.ui, text=builder.message, x=0.38, y=-0.42, origin=(0, 0), scale=0.6, color=rgb(INK), wordwrap=22)
        self.enabled = True
        for e in self.items:
            e.enabled = True
        self.status.enabled = True


class UI:
    def __init__(self):
        self.title = None
        self.hud_obj = None
        self.hud_meta = None
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
        self.hud_meta = Text("", parent=camera.ui, position=(-0.72, 0.44), origin=(-0.5, 0.5), scale=1.0, color=rgb(ACCENT))
        self.hud_obj = Text("", parent=camera.ui, position=(-0.72, 0.38), origin=(-0.5, 0.5), scale=1.0, color=rgb(INK), wordwrap=48)
        self.banner = Text("", parent=camera.ui, position=(0, 0.32), origin=(0, 0), scale=1.2, color=rgb(ACCENT), enabled=False)
        self.prompt = Text("", parent=camera.ui, position=(0, -0.42), origin=(0, 0), scale=1.2, color=rgb(TEAL), enabled=False)
        self.build_bar = Text("", parent=camera.ui, position=(0, -0.47), origin=(0, 0), scale=1.0, color=color.white, enabled=False)

        self.talk_sp = Text(parent=camera.ui, text="", y=-0.34, scale=1.0, color=rgb(ACCENT), origin=(0, 0), enabled=False)
        self.talk_tx = Text(parent=camera.ui, text="", y=-0.40, scale=0.9, color=rgb(INK), origin=(0, 0), wordwrap=42, enabled=False)
        self.talk_hint = Text(parent=camera.ui, text="E / Enter  continue", y=-0.46, scale=0.75, color=rgb(MUTED), origin=(0, 0), enabled=False)

        self.title_bits = [
            Text(parent=camera.ui, text="SEEDED PROGRAM", y=0.42, scale=0.7, color=rgb(ACCENT), origin=(0, 0)),
            Text(parent=camera.ui, text="UNDERSCORE", y=0.36, scale=1.05, color=rgb(INK), origin=(0, 0)),
            Text(parent=camera.ui, text="ENTER to wake up", y=0.30, scale=0.75, color=rgb(INK), origin=(0, 0)),
        ]

    def show_title(self, on):
        for bit in self.title_bits:
            bit.enabled = on
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
            Entity(parent=self.help, model="quad", shader=COLOR, color=color.rgba(10, 12, 20, 230), scale=(0.55, 0.32))
            lines = [
                "WASD walk · mouse look · Esc unlock mouse",
                "E talk · B build on a glowing pad",
                "Build: WASD orbit/zoom · click to place",
                "T test · Enter stamp · RMB undo",
            ]
            y = 0.1
            for line in lines:
                Text(parent=self.help, text=line, y=y, scale=0.9, color=rgb(MUTED), origin=(0, 0))
                y -= 0.06
        self.help.enabled = True
