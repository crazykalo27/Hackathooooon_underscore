"""Constants and Ursina color helpers (0–255)."""

TITLE = "UNDERSCORE"
DAY_LEN = 90.0
TALK_RANGE = 3.0
MOVE_SPEED = 7.0

# Monument Valley-ish: pastel solids, one coral accent
INK = (72, 58, 68)
PAPER = (250, 242, 230)
MUTED = (168, 148, 158)
ACCENT = (232, 96, 88)
GOLD = (240, 176, 88)
TEAL = (88, 186, 176)
STEEL = (176, 188, 204)
WOOD = (214, 154, 106)
STICKY = (214, 110, 168)
ICY = (150, 210, 230)
BOUNCY = (232, 132, 96)
HYDRO = (96, 176, 220)
CIRCUIT = (120, 196, 148)
STRUCT = (232, 176, 96)
SKY = (186, 214, 228)
SHIP_FLOOR = (242, 226, 206)
SHIP_FLOOR_B = (228, 208, 186)
SHIP_WALL = (236, 214, 198)
SHIP_ROSE = (232, 168, 156)
CREAM = (250, 240, 226)
PEACH = (236, 196, 168)
EARTH_DIRT = (214, 154, 106)
EARTH_SAND = (236, 196, 140)
EARTH_CLIFF = (196, 124, 88)
SHADOW = (210, 186, 168)

MATERIALS = {
    "wood": WOOD,
    "steel": STEEL,
    "sticky": STICKY,
    "icy": ICY,
    "bouncy": BOUNCY,
}

STARTERS = ("hydraulics", "circuits", "structure")

SHIP_LEN = 48.0
EARTH_LEN = 42.0
C2_LEN = 36.0


def rgb(c):
    from ursina import color

    if len(c) >= 4:
        return color.rgba(c[0], c[1], c[2], c[3])
    return color.rgb(c[0], c[1], c[2])
