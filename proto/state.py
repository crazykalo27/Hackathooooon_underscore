"""Persistent game flags, calendar, save file."""

from __future__ import annotations

import json
from pathlib import Path

from proto.config import DAY_LEN

SAVE_PATH = Path(__file__).resolve().parent.parent / "underscore_save.json"


class State:
    def __init__(self):
        self.flags: dict = {}
        self.map_name = "ship"
        self.day = 1
        self.day_clock = 0.0
        self.mode = "title"  # title | play | talk | build | fade | pick
        self.banner = ""
        self.banner_t = 0.0
        self.flash_node = ""
        self.flash_t = 0.0
        self.pick_focus = 0  # starter picker index

    def inventions(self):
        return list(self.flags.get("inventions") or [])

    def add_invention(self, name, zone, day):
        inv = self.inventions()
        inv.append({"name": name, "zone": zone, "day": day})
        self.flags["inventions"] = inv[-24:]

    def flash(self, node, seconds=3.2):
        self.flash_node = node
        self.flash_t = seconds

    def branch_xp(self, branch):
        xp = self.flags.get("branch_xp") or {}
        return int(xp.get(branch, 0))

    def add_branch_xp(self, branch, amount=1):
        xp = dict(self.flags.get("branch_xp") or {})
        bias = 2 if self.flags.get("starter") == branch else 1
        xp[branch] = int(xp.get(branch, 0)) + amount * bias
        self.flags["branch_xp"] = xp
        # Bias unlocks: starter (or enough XP) opens the next toy
        if branch == "hydraulics" and xp[branch] >= 1:
            self.flags["unlock_spring"] = True
        if branch == "circuits" and xp[branch] >= 1:
            self.flags["unlock_circuit_kit"] = True

    def flag(self, key, default=False):
        return self.flags.get(key, default)

    def set_flag(self, key, value=True):
        self.flags[key] = value

    def money(self):
        return int(self.flags.get("money", 0))

    def add_money(self, n):
        self.flags["money"] = self.money() + n

    def tick_day(self, dt):
        if self.mode != "play":
            return
        self.day_clock += dt
        if self.day_clock >= DAY_LEN:
            self.day += 1
            self.day_clock = 0.0
            self._elevator_tick()

    def advance_day(self):
        self.day += 1
        self.day_clock = 0.0
        self._elevator_tick()

    def _elevator_tick(self):
        start = self.flags.get("elevator_start_day")
        if self.flag("c2_elevator_started") and start is not None:
            if self.day >= int(start) + 2 and not self.flag("c2_elevator_done"):
                self.set_flag("c2_elevator_done")
                self.add_money(80)
                self.banner = "Colony 2 is on the network."
                self.banner_t = 4.0
        if self.flag("c2_elevator_done") and self.flag("icy") and not self.flag("storm"):
            self.set_flag("storm")
            self.banner = "Dust storm on Colony 1."
            self.banner_t = 4.0

    def save(self, x=0.0, z=0.0):
        data = {
            "flags": {k: v for k, v in self.flags.items() if not str(k).startswith("_")},
            "map": self.map_name,
            "x": x,
            "z": z,
            "day": self.day,
            "day_clock": self.day_clock,
        }
        try:
            SAVE_PATH.write_text(json.dumps(data, indent=2))
        except OSError:
            pass

    def load(self):
        try:
            data = json.loads(SAVE_PATH.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        self.flags = data.get("flags") or {}
        self.map_name = data.get("map") or "ship"
        self.day = data.get("day") or 1
        self.day_clock = float(data.get("day_clock") or 0)
        return float(data.get("x") or 3.0), float(data.get("z") or 0.0)

    @staticmethod
    def has_save():
        return SAVE_PATH.exists()
