"""Constants and Ursina color helpers (0–255)."""

from pathlib import Path

TITLE = "UNDERSCORE"
_FONT = Path(__file__).resolve().parent / "fonts" / "PixelifySans-Regular.ttf"
_FONT_FALLBACK = Path(__file__).resolve().parent / "fonts" / "Tiny5-Regular.ttf"
FONT = str(_FONT if _FONT.exists() else (_FONT_FALLBACK if _FONT_FALLBACK.exists() else "VeraMono.ttf"))
DAY_LEN = 90.0
TALK_RANGE = 3.0
MOVE_SPEED = 7.0

# Space-age hull: void navy, cyan trim, ice lights. Pads keep their own colors.
INK = (22, 28, 42)
PAPER = (228, 240, 252)
MUTED = (122, 148, 174)
ACCENT = (240, 88, 102)
GOLD = (255, 206, 96)
TEAL = (64, 210, 214)
STEEL = (168, 196, 224)
BRASS = (96, 206, 236)
BRASS_D = (48, 118, 158)
IRON = (32, 44, 68)
IRON_B = (44, 60, 88)
COPPER = (78, 128, 196)
PATINA = (48, 196, 176)
LAMP = (160, 228, 255)
WOOD = (214, 154, 106)
STICKY = (214, 110, 168)
ICY = (150, 210, 230)
BOUNCY = (232, 132, 96)
HYDRO = (96, 176, 220)
CIRCUIT = (120, 196, 148)
STRUCT = (232, 176, 96)
SKY = (176, 216, 248)
SPACE = (6, 10, 22)

# Pocket Build UI — cream cards, slim navy chips, toy pips
UI_INK = (56, 62, 78)
UI_MUTED = (118, 130, 148)
UI_CREAM = (255, 248, 236)
UI_CREAM_D = (236, 226, 210)
UI_CHIP = (42, 56, 92)
UI_CHIP_DEEP = (28, 38, 64)
UI_WOOD = (196, 140, 88)
UI_GOLD = (232, 188, 72)
UI_GRASS = (168, 204, 88)
UI_ROOF = (72, 120, 176)
UI_CLAY = (196, 92, 72)
UI_PEACH = (236, 196, 176)
UI_SHADOW = (24, 30, 42)
STAR = (236, 244, 255)
STAR_DIM = (120, 156, 210)
SHIP_FLOOR = (18, 26, 42)
SHIP_FLOOR_B = (26, 38, 58)
SHIP_WALL = (36, 50, 78)
SHIP_ROSE = (42, 56, 92)
CREAM = (236, 246, 255)
PEACH = (236, 196, 176)
EARTH_DIRT = (214, 154, 106)
EARTH_SAND = (236, 196, 140)
EARTH_CLIFF = (196, 124, 88)
SHADOW = (10, 14, 24)

STICKY_WOOD = (196, 120, 140)
STICKY_STEEL = (168, 140, 196)

MATERIALS = {
    "wood": WOOD,
    "steel": STEEL,
    "sticky": STICKY,
    "icy": ICY,
    "bouncy": BOUNCY,
    "sticky_wood": STICKY_WOOD,
    "sticky_steel": STICKY_STEEL,
}

# Catalog nodes that flash the skill-tree UI when unlocked
TREE_NODES = (
    "first_invention",
    "trial_hydraulics",
    "trial_circuits",
    "trial_structure",
    "starter",
    "capstone",
    "sticky",
    "icy",
    "bouncy",
    "registered",
)

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
CAM_PITCH_MIN = 8.0
CAM_PITCH_MAX = 80.0
CAM_DIST = 26.0
CAM_DIST_MIN = 4.0
CAM_DIST_MAX = 400.0
# Play stays at or under 20%. Crossing that eases to map mode at 40%.
CAM_PLAY_MAX = CAM_DIST_MAX * 0.20
CAM_MAP_MIN = CAM_DIST_MAX * 0.40
CAM_LOOK_Y = 1.15


def rgb(c):
    from ursina import color

    if len(c) >= 4:
        return color.rgba(c[0], c[1], c[2], c[3])
    return color.rgb(c[0], c[1], c[2])
