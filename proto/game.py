"""Game orchestrator — modes, input, travel."""

from __future__ import annotations

from ursina import Entity, color, mouse, time

from proto import story
from proto.builder import Builder
from proto.config import EARTH_LEN, HALL_HALF, HULL_CEIL, SHIP_LEN, WALK_Z
from proto.player import Player
from proto.state import State
from proto.ui import UI
from proto.world import World


class Game(Entity):
    def __init__(self, autoload=True):
        super().__init__()
        self.state = State()
        self.world = World()
        self.builder = Builder()
        self.ui = UI()
        self.player = None
        self.dialogue = []
        self.d_i = 0
        self.typed = 0.0
        self.cmd = None
        self.near_npc = None
        self.near_zone = None
        self.fade = 0.0
        self.fade_dir = 0
        self.fade_cb = None
        self.fade_hold = 0.0
        self.fade_title = ""
        self.fade_sub = ""
        from proto.visuals import COLOR

        self.fade_veil = Entity(
            parent=__import__("ursina", fromlist=["camera"]).camera.ui,
            model="quad",
            shader=COLOR,
            color=color.rgba(10, 12, 18, 0),
            scale=2,
            z=-1,
            enabled=False,
        )
        self.fade_label = None
        if autoload:
            self.boot_world()
            self.boot_player()

    def boot_world(self):
        self.world.load("ship", self.state.flags)

    def boot_player(self):
        if self.player:
            return
        self.player = Player(position=(5.5, 0, 0))
        self.player.disable()
        self.ui.show_title(True)

    def update(self):
        if self.player is None:
            return
        dt = time.dt
        if self.state.banner_t > 0:
            self.state.banner_t -= dt

        if self.state.mode == "fade":
            self._update_fade(dt)
            self._draw_ui()
            return

        if self.state.mode == "play":
            self.state.tick_day(dt)
            self.near_npc = self.world.nearest_npc(self.player)
            self.near_zone = self.world.zone_here(self.player)
            # keep on floor maps
            length = story.map_len(self.state.map_name)
            self.player.x = max(1.0, min(length - 1.5, self.player.x))
            zlim = WALK_Z if self.state.map_name == "ship" else 7.4
            self.player.z = max(-zlim, min(zlim, self.player.z))
            if self.state.map_name == "earth" and self.state.flag("ravine") and self.player.x > EARTH_LEN - 2.5:
                if not self.state.flag("c2_elevator_done"):
                    self.begin_fade(self._to_c2, "East trail", "Heat instead of a gap.")
            if self.state.map_name == "c2" and self.player.x < 1.2:
                if self.state.flag("c2_elevator_done"):
                    self.player.x = 2
                else:
                    self.begin_fade(self._to_earth_east, "Back to Colony 1", "")
            if self.state.map_name == "earth" and 14 < self.player.x < 22 and self.player.y < -0.5:
                self.player.teleport(12, 0)

        if self.state.mode == "build":
            self.builder.update()

        if self.state.mode == "talk" and self.dialogue and self.d_i < len(self.dialogue):
            self.typed = min(len(self.dialogue[self.d_i][1]), self.typed + dt * 60)

        self._draw_ui()

    def _draw_ui(self):
        self.ui.refresh(
            self.state,
            near_npc=self.near_npc,
            near_zone=self.near_zone,
            dialogue=self.dialogue,
            d_i=self.d_i,
            typed=self.typed,
            builder=self.builder if self.state.mode == "build" else None,
        )
        if self.state.mode == "fade":
            self.fade_veil.enabled = True
            a = int(min(1, self.fade) * 255)
            self.fade_veil.color = color.rgba(10, 12, 18, a)
        else:
            self.fade_veil.enabled = False

    def input(self, key):
        if self.player is None:
            return
        if key == "escape":
            if self.state.mode == "build":
                self._leave_build()
            elif self.state.mode == "talk":
                self._end_talk(cancel=True)
            elif self.state.mode == "fade":
                self._skip_fade()
            elif mouse.locked:
                mouse.locked = False
            elif self.state.mode == "play":
                mouse.locked = True
            return

        if self.state.mode == "title":
            if key in ("enter", "space", "e"):
                self.wake()
            if key == "c" and State.has_save():
                self.continue_save()
            return

        if key == "h":
            self.ui.toggle_help()
        if key == "f5":
            self.state.save(self.player.x, self.player.z)
            self._banner("Saved.")

        if self.state.mode == "talk" and key in ("e", "enter", "space"):
            self._advance_talk()
        if self.state.mode == "fade" and key in ("e", "enter", "space"):
            self._skip_fade()

        if self.state.mode == "play":
            if key == "e":
                if self.near_npc:
                    self.start_talk(self.near_npc)
                else:
                    self.enter_build()
            if key == "b":
                self.enter_build()

        if self.state.mode == "build":
            if key == "left mouse down":
                if self.ui.build_menu.consume_click(self.builder, self.state.flags):
                    return
                self.builder.place()
            if key == "right mouse down" or key == "backspace":
                self.builder.delete_last()
            if key == "t":
                self.builder.test()
            if key == "r":
                z = self.builder.zone
                self.builder.enter(z, self.state.flags, hull=self._hull_bounds())
            if key == "enter":
                self.stamp()
            if key == "tab":
                self.builder.cycle(self.state.flags)
            if key in ("1", "2", "3", "4", "5"):
                names = self.builder.mats(self.state.flags)
                idx = int(key) - 1
                if idx < len(names):
                    self.builder.set_mat(names[idx], self.state.flags)
            if key == "scroll up":
                self.builder.nudge_pitch(8)
            if key == "scroll down":
                self.builder.nudge_pitch(-8)

    def wake(self):
        self.state.mode = "play"
        self.ui.show_title(False)
        self.player.teleport(5.5, 0)
        self.player.rotation_y = 90
        self.player.enable()
        self._banner("You are in the academy hall. Walk to Mara (coral), press E.")

    def continue_save(self):
        pos = self.state.load()
        if not pos:
            return
        self.world.load(self.state.map_name, self.state.flags)
        self.player.teleport(pos[0], pos[1])
        self.state.mode = "play"
        self.ui.show_title(False)
        self.player.enable()
        self._banner("Continued.")

    def start_talk(self, npc):
        self.state.flags["_map"] = self.state.map_name
        raw = story.lines(npc.talk_id, self.state.flags, self.state.map_name)
        self.dialogue = [(a, b) for a, b in raw if a != "*"]
        self.cmd = next((b for a, b in raw if a == "*"), None)
        self.d_i = 0
        self.typed = 0.0
        self.state.mode = "talk"
        self.player.disable()

    def _advance_talk(self):
        if not self.dialogue:
            self._end_talk()
            return
        full = self.dialogue[self.d_i][1]
        if self.typed < len(full):
            self.typed = float(len(full))
            return
        self.d_i += 1
        self.typed = 0.0
        if self.d_i >= len(self.dialogue):
            self._end_talk()

    def _end_talk(self, cancel=False):
        cmd = None if cancel else self.cmd
        self.cmd = None
        self.dialogue = []
        if cmd == "elevator_down":
            self.begin_fade(self._to_earth, "The cable sings.", "Most never feel this.")
        elif cmd == "elevator_up":
            self.begin_fade(self._to_ship, "Hull light.", "Home, sort of.")
        elif cmd == "walk_c2":
            self.begin_fade(self._to_c2, "East trail.", "")
        elif cmd == "flare_up":
            self.begin_fade(self._flare, "Flare.", "One way.")
        elif cmd == "sleep":
            self.state.advance_day()
            self.state.mode = "play"
            self.player.enable()
            self._banner(f"Day {self.state.day}.")
        else:
            self.state.mode = "play"
            self.player.enable()
            if self.state.flag("met_mara") and not self.state.flag("first_invention"):
                self._banner("Yellow WORKSHOP pad. Stand on it, press B.")
            # refresh world if mentors should appear
            if self.state.flag("first_invention"):
                x, z = self.player.x, self.player.z
                self.world.load(self.state.map_name, self.state.flags)
                self.player.teleport(x, z)
            self.state.save(self.player.x, self.player.z)

    def enter_build(self):
        zone = self.world.zone_here(self.player)
        if not zone:
            self._banner("Stand on a glowing pad, then B.")
            return
        if zone.gate_flag and not self.state.flag(zone.gate_flag):
            self._banner(zone.gate_msg)
            return
        self.builder.enter(zone, self.state.flags, hull=self._hull_bounds())
        self.state.mode = "build"
        self.player.disable()
        self.player.visible = False
        self._banner("WASD orbit · scroll tilts. Click to place.")

    def stamp(self):
        if not self.builder.goal_done:
            self._banner("Press T first — wait for 'It holds!'")
            return
        key = self.builder.zone.key
        info = story.STAMP_FLAGS.get(key)
        if info:
            flag, msg, pay = info
            self.state.set_flag(flag)
            self.state.add_money(pay)
            self._banner(msg)
            if key == "pylon":
                self.state.flags["elevator_start_day"] = self.state.day
        self._leave_build()
        x, z = self.player.x, self.player.z
        self.world.load(self.state.map_name, self.state.flags)
        self.player.teleport(x, z)
        self.state.save(x, z)

    def _leave_build(self):
        self.builder.leave()
        self.state.mode = "play"
        self.player.visible = True
        self.player.enable()
        self.player.snap_camera()

    def _hull_bounds(self):
        if self.state.map_name != "ship":
            z = self.world.zone_here(self.player) or self.builder.zone
            if not z:
                return None
            return (
                z.x - z.w * 0.7,
                z.x + z.w * 0.7,
                0.5,
                12.0,
                z.z - z.d * 0.7,
                z.z + z.d * 0.7,
            )
        m = HALL_HALF - 0.75
        return (0.4, SHIP_LEN - 0.7, 0.55, HULL_CEIL - 0.45, -m, m)

    def begin_fade(self, cb, title, sub):
        self.fade_dir = 1
        self.fade = 0
        self.fade_cb = cb
        self.fade_hold = 0
        self.fade_title = title
        self.fade_sub = sub
        self.state.mode = "fade"
        self.player.disable()

    def _update_fade(self, dt):
        if self.fade_dir == 1:
            self.fade = min(1.0, self.fade + dt * 1.3)
            if self.fade >= 1.0:
                if self.fade_cb:
                    self.fade_cb()
                    self.fade_cb = None
                self.fade_hold += dt
                if self.fade_hold >= 0.9:
                    self.fade_dir = -1
        elif self.fade_dir == -1:
            self.fade = max(0.0, self.fade - dt * 1.3)
            if self.fade <= 0:
                self.fade_dir = 0
                self.state.mode = "play"
                self.player.enable()

    def _skip_fade(self):
        if self.fade_dir == 1 and self.fade_cb:
            self.fade_cb()
            self.fade_cb = None
        self.fade = 0
        self.fade_dir = 0
        self.state.mode = "play"
        self.player.enable()

    def _swap(self, name, x):
        self.state.map_name = name
        self.world.load(name, self.state.flags)
        self.player.teleport(x, 0)

    def _to_earth(self):
        self.state.set_flag("deployed")
        self.state.flags["left_ship_day"] = self.state.day
        self.state.day = max(self.state.day, 2)
        self._swap("earth", 3)
        self._banner("COLONY 1 — only elevator.")

    def _to_ship(self):
        self.state.day += 1
        self.state.day_clock = 0
        self._swap("ship", SHIP_LEN - 4)
        self.state._elevator_tick()
        self._banner("Ship lab.")

    def _to_c2(self):
        self.state.set_flag("discovered_c2")
        if self.state.flag("flared_early") and not self.state.flag("shade"):
            self.state.set_flag("nima_left")
        self._swap("c2", 2.5)
        self._banner("COLONY 2.")

    def _to_earth_east(self):
        self._swap("earth", EARTH_LEN - 3)

    def _flare(self):
        self._swap("ship", SHIP_LEN - 4)
        self.state._elevator_tick()
        self._banner("Flare. No return until cable.")

    def _banner(self, text, t=3.0):
        self.state.banner = text
        self.state.banner_t = t
