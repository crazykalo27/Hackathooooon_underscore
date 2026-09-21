"""Story data: zones, NPCs, dialogue, objectives."""

from __future__ import annotations

from dataclasses import dataclass

from proto.config import (
    ACCENT,
    CIRCUIT,
    C2_LEN,
    EARTH_LEN,
    GOLD,
    HYDRO,
    SHIP_LEN,
    STRUCT,
    TEAL,
)


@dataclass
class Zone:
    key: str
    x: float
    z: float
    w: float
    d: float
    goal: str
    label: str
    color: tuple = TEAL
    gap: tuple | None = None
    lift_y: float = 1.2
    gate_flag: str | None = None
    gate_msg: str = ""

    def contains(self, px, pz):
        return abs(px - self.x) <= self.w * 0.5 + 0.9 and abs(pz - self.z) <= self.d * 0.5 + 0.9


@dataclass
class NpcDef:
    id: str
    name: str
    x: float
    color: tuple
    talk: str
    z: float = 0.0
    rot: float = -90  # yaw; 0 faces +Z
    show_if: str | None = None  # flag required to appear
    hide_if: str | None = None


SHIP_ZONES = [
    Zone("workshop", 22, 0, 12, 12, "shelf", "Stack a shelf — C weld, T drop crate", GOLD,
         gate_flag="met_mara", gate_msg="Talk to Mara by the bunk first."),
    Zone("hydro", 38, 0, 10, 10, "lift", "Piston or spring under crate, T to lift", HYDRO,
         gate_flag="first_invention", gate_msg="Workshop first.", lift_y=1.8),
    Zone("circuit", 52, 0, 10, 10, "roll", "Battery → wire/switch → motor, T to roll", CIRCUIT,
         gate_flag="first_invention", gate_msg="Workshop first."),
    Zone("struct", 68, 0, 12, 10, "span", "Brace across the gap — weak spans snap", STRUCT, gap=(65.5, 70.5),
         gate_flag="first_invention", gate_msg="Workshop first."),
    Zone("lab", 82, 0, 10, 10, "free", "Capstone — include a starter part", TEAL,
         gate_flag="starter", gate_msg="Pick a starter mentor first."),
]

EARTH_ZONES = [
    Zone("ravine", 20, 0, 20, 16, "span", "Span the ravine", ACCENT, gap=(14, 22),
         gate_flag="met_dust", gate_msg="Talk to Dust first."),
    Zone("storm", 8, 0, 10, 10, "shelf", "Clinic door", TEAL,
         gate_flag="storm", gate_msg="No storm yet."),
]

C2_ZONES = [
    Zone("shade", 12, 0, 12, 10, "shelf", "Shade the tanks", ACCENT,
         gate_flag="met_reed", gate_msg="Talk to Reed first."),
    Zone("pylon", 26, 0, 14, 10, "span", "Pylon footing", ACCENT, gap=(24, 28),
         gate_flag="shade", gate_msg="Shade first."),
]

SHIP_NPCS = [
    NpcDef("cot", "Cot", 2.0, (176, 156, 168), "cot", z=-3.7, rot=70),
    NpcDef("mara", "Mara", 5.5, (236, 124, 104), "mara", z=-3.8, rot=10),
    NpcDef("jun", "Jun", 8.6, (232, 168, 176), "jun", z=9.2, rot=200),
    NpcDef("rio", "Rio", 14.1, (104, 176, 204), "rio", z=-11.2, rot=180),
    NpcDef("olia", "Olia", 31.8, HYDRO, "olia", z=6.2, rot=-70, show_if="first_invention"),
    NpcDef("vex", "Vex", 54.6, CIRCUIT, "vex", z=-6.2, rot=95, show_if="first_invention"),
    NpcDef("kenji", "Kenji", 63.4, STRUCT, "kenji", z=6.0, rot=-50, show_if="first_invention"),
    NpcDef("sila", "Sila", 76.4, (196, 160, 232), "sila", z=-6.1, rot=55, show_if="first_invention"),
    NpcDef("lift", "Elevator", 87.8, ACCENT, "elevator", z=4.0, rot=-90),
]

EARTH_NPCS = [
    NpcDef("lift", "Elevator", 2.4, ACCENT, "elevator", z=2.4, rot=90),
    NpcDef("dust", "Dust", 7.4, (196, 124, 72), "dust", z=-3.6, rot=40),
    NpcDef("ivy", "Ivy", 5.2, (170, 150, 190), "ivy", z=3.8, rot=160),
    NpcDef("pax", "Pax", 11.4, (150, 110, 80), "pax", z=4.2, rot=-20),
    NpcDef("sample", "Goo", 26.2, (214, 86, 168), "sample", z=-2.8, hide_if="sample"),
    NpcDef("trail", "East", 37.6, (180, 140, 90), "trail", z=2.2, rot=-90, show_if="ravine"),
]

C2_NPCS = [
    NpcDef("flare", "Flare", 2.2, (255, 140, 80), "flare", z=-3.2, rot=50),
    NpcDef("reed", "Reed", 8.6, (80, 150, 170), "reed", z=4.4, rot=200),
    NpcDef("nima", "Nima", 14.4, (200, 150, 110), "nima", z=-4.0, rot=15, hide_if="nima_left"),
    NpcDef("pylon", "Pylon", 26.4, ACCENT, "pylon", z=3.6, rot=-90),
    NpcDef("frost", "Frost", 30.6, (150, 210, 230), "frost", z=-3.8, rot=130, hide_if="icy_sample"),
]


def zones_for(map_name):
    return {"ship": SHIP_ZONES, "earth": EARTH_ZONES, "c2": C2_ZONES}.get(map_name, SHIP_ZONES)


def npcs_for(map_name):
    return {"ship": SHIP_NPCS, "earth": EARTH_NPCS, "c2": C2_NPCS}.get(map_name, SHIP_NPCS)


def map_len(map_name):
    return {"ship": SHIP_LEN, "earth": EARTH_LEN, "c2": C2_LEN}.get(map_name, SHIP_LEN)


def objective(flags):
    if not flags.get("met_mara"):
        return "Talk to Mara by the bunk. WASD walk, E talk."
    if not flags.get("first_invention"):
        return "Yellow workshop. B, place, C weld, T, Enter."
    if not flags.get("trial_hydraulics"):
        return "Blue hydraulics — Olia. Piston or spring lift."
    if not flags.get("trial_circuits"):
        return "Green circuits — Vex. Battery, wire, switch, motor."
    if not flags.get("trial_structure"):
        return "Gold structure — Kenji. Span the gap."
    if not flags.get("starter"):
        return "All trials done. Talk to a mentor — pick a starter."
    if not flags.get("capstone"):
        return "Lab pad — build with a starter part, then stamp."
    if not flags.get("registered"):
        return "Talk to Sila to register your capstone."
    if not flags.get("deployed"):
        return "Elevator at the far end — ride to Earth."
    if not flags.get("met_dust"):
        return "Colony 1 — talk to Dust."
    if not flags.get("ravine"):
        return "Span the ravine (B on the gap)."
    if not flags.get("sample"):
        return "Take the sticky sample on the far ledge."
    if not flags.get("sticky"):
        return "Elevator up — register sticky with Sila."
    if not flags.get("discovered_c2"):
        return "East trail to Colony 2."
    if not flags.get("shade"):
        return "Colony 2 — shade the tanks."
    if not flags.get("c2_elevator_done"):
        return "Pylon / wait two days / flare."
    return "Earth is not finished."


def all_trials(flags):
    return flags.get("trial_hydraulics") and flags.get("trial_circuits") and flags.get("trial_structure")


def lines(talk_id, flags, map_name="ship"):
    """Return dialogue rows; speaker '*' means travel command."""
    s = flags.get("starter")
    if talk_id == "mara":
        if flags.get("met_mara"):
            if flags.get("first_invention"):
                return [("Mara", "Trials next. Taste all three. Then pick a starter.")]
            return [("Mara", "Yellow workshop pad. B to build. Everyone else is extra.")]
        flags["met_mara"] = True
        return [
            ("Mara", "Up. The Seeded Program does not wait for beautiful sleep."),
            ("You", "I still feel like I stole someone else's slot."),
            ("Mara", "You built through it. That is why they want you on Earth."),
            ("Mara", "Invent on the yellow pad. Talk to the others if you want — you do not have to."),
        ]
    if talk_id == "rio":
        flags["met_rio"] = True
        if flags.get("first_invention"):
            return [("Rio", "You stamped something. Good. Now the mentors will eat you alive.")]
        return [
            ("Rio", "They posted the list. My name is not on it. Yours is underlined."),
            ("You", "I can ask—"),
            ("Rio", "Do not. Yellow pad ahead. Build a shelf that holds. B, click, T, Enter."),
        ]
    if talk_id == "olia":
        if flags.get("starter") == "hydraulics":
            return [("Olia", "Pistons and springs. Earth has weight.")]
        if flags.get("starter"):
            return [("Olia", "Not my bay.")]
        if not flags.get("trial_hydraulics"):
            return [("Olia", "My pad. Piston or spring under the crate. C weld, T lift, Enter.")]
        if all_trials(flags) and not s:
            return [("Olia", "All trials done. Open the starter pick — choose Hydraulics if it felt right."), ("*", "open_pick")]
        return [("Olia", "Trial stamped. Finish all three, then we pick a starter.")]
    if talk_id == "vex":
        if flags.get("starter") == "circuits":
            return [("Vex", "Battery. Wire. Switch. Motor.")]
        if flags.get("starter"):
            return [("Vex", "Go on.")]
        if not flags.get("trial_circuits"):
            return [("Vex", "Chain: battery touches wire or switch, then motor. T rolls the crate.")]
        if all_trials(flags) and not s:
            return [("Vex", "All three stamped. Pick Circuits on the starter screen if that is you."), ("*", "open_pick")]
        return [("Vex", "Stamped. Two more trials, then pick.")]
    if talk_id == "kenji":
        if flags.get("starter") == "structure":
            return [("Kenji", "Span first. Your braces hold harder now.")]
        if flags.get("starter"):
            return [("Kenji", "Fine.")]
        if not flags.get("trial_structure"):
            return [("Kenji", "Bridge the gap. Weak wood snaps — steel or a plate helps.")]
        if all_trials(flags) and not s:
            return [("Kenji", "Trials done. Pick Structure if spanning is your language."), ("*", "open_pick")]
        return [("Kenji", "Stamped.")]
    if talk_id == "sila":
        if flags.get("sample") and not flags.get("sticky"):
            flags["sticky"] = True
            return [("Sila", "Sticky is catalog. Unlimited now. That is the loop.")]
        if flags.get("icy_sample") and not flags.get("icy"):
            flags["icy"] = True
            flags["money"] = flags.get("money", 0) + 40
            return [("Sila", "Icy is catalog.")]
        if flags.get("bouncy_sample") and not flags.get("bouncy"):
            flags["bouncy"] = True
            flags["money"] = flags.get("money", 0) + 40
            return [("Sila", "Bouncy is a word now.")]
        if flags.get("starter") and not flags.get("capstone"):
            return [("Sila", "Capstone on my pad — use a part from your starter branch.")]
        if flags.get("starter") and not flags.get("registered"):
            flags["registered"] = True
            return [("Sila", "Registered. Elevator is far right. That is the loop, named.")]
        if flags.get("registered") and not flags.get("deployed"):
            return [("Sila", "Go.")]
        return [("Sila", "Workshop, trials, starter pick, capstone — then I stamp.")]
    if talk_id == "elevator":
        if map_name == "earth":
            return [("Elevator", "Ship?"), ("*", "elevator_up")]
        if map_name == "c2":
            if flags.get("c2_elevator_done"):
                return [("Elevator", "Ship?"), ("*", "elevator_up")]
            return [("Elevator", "No cable. Flare west.")]
        if flags.get("registered"):
            return [("Elevator", "One drop. Hold the rail."), ("*", "elevator_down")]
        return [("Elevator", "Sila stamps first.")]
    if talk_id == "dust":
        flags["met_dust"] = True
        if flags.get("ravine"):
            return [("Dust", "You spanned it. Pink goo east.")]
        return [("Dust", "Ravine. Walk right. B at the gap.")]
    if talk_id == "sample":
        if flags.get("sample"):
            return [("Goo", "(packed)")]
        if not flags.get("ravine"):
            return [("Goo", "(not yet)")]
        flags["sample"] = True
        return [("You", "It clings."), ("Goo", "(Sila.)")]
    if talk_id == "trail":
        if flags.get("c2_elevator_done"):
            return [("East", "Ride the ship.")]
        return [("East", "A well with no cable."), ("*", "walk_c2")]
    if talk_id == "jun":
        flags["met_jun"] = True
        return [("Jun", "Come back with all your hands.")]
    if talk_id == "cot":
        return [("Cot", "Sleep."), ("*", "sleep")]
    if talk_id == "flare":
        if not flags.get("shade"):
            flags["flared_early"] = True
        return [("Flare", "One-way ship."), ("*", "flare_up")]
    if talk_id == "reed":
        flags["met_reed"] = True
        if flags.get("shade"):
            return [("Reed", "Pylon east.")]
        return [("Reed", "Shade the tanks.")]
    if talk_id == "nima":
        if flags.get("c2_elevator_started") and not flags.get("bouncy_sample"):
            flags["bouncy_sample"] = True
            return [("Nima", "Take the husk.")]
        return [("Nima", "Build the shade.")]
    if talk_id == "pylon":
        if flags.get("c2_elevator_done"):
            return [("Pylon", "Ride?"), ("*", "elevator_up")]
        if flags.get("c2_elevator_started"):
            return [("Pylon", "Curing.")]
        return [("Pylon", "B on the footing.")]
    if talk_id == "frost":
        if not flags.get("shade"):
            return [("Frost", "(shade first)")]
        flags["icy_sample"] = True
        return [("Frost", "(cold.)")]
    if talk_id == "ivy":
        flags["met_ivy"] = True
        return [("Ivy", "Some of us were told no.")]
    if talk_id == "pax":
        flags["met_pax"] = True
        return [("Pax", "Stack. Do not weld.")]
    return [("???", "...")]


STAMP_FLAGS = {
    "workshop": ("first_invention", "First invention stamped. Mentors unlock down the hall.", 15),
    "hydro": ("trial_hydraulics", "Hydraulics stamped.", 10),
    "circuit": ("trial_circuits", "Circuits stamped.", 10),
    "struct": ("trial_structure", "Structure stamped.", 10),
    "lab": ("capstone", "Capstone holds. Talk to Sila.", 15),
    "ravine": ("ravine", "Ravine holds.", 40),
    "shade": ("shade", "Tanks shaded.", 50),
    "pylon": ("c2_elevator_started", "Pylon poured. Two days.", 30),
    "storm": ("storm_door", "Clinic held.", 35),
}
