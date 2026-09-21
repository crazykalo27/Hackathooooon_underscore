"""Constants and Ursina color helpers (0–255)."""

from pathlib import Path

TITLE = "UNDERSCORE"
_FONT = Path(__file__).resolve().parent / "fonts" / "Tiny5-Regular.ttf"
FONT = str(_FONT) if _FONT.exists() else "VeraMono.ttf"
DAY_LEN = 90.0
TALK_RANGE = 3.0
MOVE_SPEED = 7.0

# Steampunk hull: iron, brass, copper, lamp-warm. Pads keep their own colors.
INK = (48, 36, 32)
PAPER = (236, 220, 196)
MUTED = (148, 124, 108)
ACCENT = (196, 78, 58)
GOLD = (196, 142, 64)
TEAL = (64, 128, 118)
STEEL = (176, 188, 204)
BRASS = (176, 128, 58)
BRASS_D = (132, 92, 44)
IRON = (62, 52, 46)
IRON_B = (78, 66, 56)
COPPER = (148, 82, 54)
PATINA = (58, 108, 98)
LAMP = (232, 156, 72)
WOOD = (214, 154, 106)
STICKY = (214, 110, 168)
ICY = (150, 210, 230)
BOUNCY = (232, 132, 96)
HYDRO = (96, 176, 220)
CIRCUIT = (120, 196, 148)
STRUCT = (232, 176, 96)
SKY = (186, 214, 228)
SPACE = (8, 10, 18)
STAR = (236, 232, 220)
STAR_DIM = (148, 164, 198)
SHIP_FLOOR = (58, 50, 44)
SHIP_FLOOR_B = (72, 62, 54)
SHIP_WALL = (68, 58, 52)
SHIP_ROSE = (86, 54, 48)
CREAM = (250, 240, 226)
PEACH = (236, 196, 168)
EARTH_DIRT = (214, 154, 106)
EARTH_SAND = (236, 196, 140)
EARTH_CLIFF = (196, 124, 88)
SHADOW = (42, 36, 32)

MATERIALS = {
    "wood": WOOD,
    "steel": STEEL,
    "sticky": STICKY,
    "icy": ICY,
    "bouncy": BOUNCY,
}

STARTERS = ("hydraulics", "circuits", "structure")

SHIP_LEN = 92.0
EARTH_LEN = 48.0
C2_LEN = 42.0
HALL_HALF = 14.0
HULL_CEIL = 8.1
WALK_Z = HALL_HALF - 0.8

# God-view camera — orbit around a look point, never under the player
CAM_FOV = 52
CAM_YAW = 42.0
CAM_PITCH = 38.0
CAM_PITCH_MIN = 22.0
CAM_PITCH_MAX = 80.0
CAM_DIST = 26.0
CAM_DIST_MIN = 4.0
CAM_DIST_MAX = 400.0
CAM_EDGE = 0.25
CAM_LOOK_Y = 1.15


def rgb(c):
    from ursina import color

    if len(c) >= 4:
        return color.rgba(c[0], c[1], c[2], c[3])
    return color.rgb(c[0], c[1], c[2])
