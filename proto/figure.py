"""Chibi toy people — chubby low-poly, big head, blob shadow."""

from __future__ import annotations

from proto.config import PEACH
from proto.visuals import solid

BLUSH = (232, 146, 132)
EYE = (48, 42, 58)
SHINE = (255, 248, 236)


def shade(col, k):
    return tuple(max(0, min(255, int(c * k))) for c in col[:3])


def attach(parent, shirt, skin=PEACH, pants=None, hair=None, accent=None, shoes=None, look=0):
    pants = pants or shade(shirt, 0.72)
    hair = hair or shade(shirt, 0.45)
    accent = accent or shirt
    shoes = shoes or shade(pants, 0.55)
    look = int(look) % 5

    def part(col, pos, scale, model="sphere"):
        if isinstance(scale, (int, float)):
            scale = (scale, scale, scale)
        return solid(col, parent=parent, model=model, position=pos, scale=scale, collider=None)

    part((48, 44, 58), (0, 0.03, 0), (0.78, 0.06, 0.52))
    part(pants, (-0.13, 0.30, 0), (0.18, 0.46, 0.18))
    part(pants, (0.13, 0.30, 0), (0.18, 0.46, 0.18))
    part(shoes, (-0.13, 0.08, 0.05), (0.22, 0.12, 0.30))
    part(shoes, (0.13, 0.08, 0.05), (0.22, 0.12, 0.30))
    part(shirt, (0, 0.82, 0), (0.56, 0.62, 0.42))
    part(accent, (0, 1.02, 0.04), (0.30, 0.14, 0.24))
    part(shirt, (-0.38, 0.78, 0), (0.18, 0.40, 0.18))
    part(shirt, (0.38, 0.78, 0), (0.18, 0.40, 0.18))
    part(skin, (-0.40, 0.56, 0.02), 0.15)
    part(skin, (0.40, 0.56, 0.02), 0.15)
    part(skin, (0, 1.36, 0.02), (0.52, 0.50, 0.48))

    if look == 0:
        part(hair, (0, 1.54, -0.02), (0.56, 0.30, 0.52))
    elif look == 1:
        part(hair, (0.02, 1.56, -0.02), (0.40, 0.24, 0.38))
        part(hair, (0.10, 1.72, 0.0), (0.18, 0.20, 0.18))
        part(shade(pants, 0.8), (0, 0.78, -0.22), (0.22, 0.26, 0.16))
    elif look == 2:
        part(hair, (0.08, 1.50, -0.02), (0.54, 0.24, 0.50))
        part(hair, (0.24, 1.28, 0.02), (0.16, 0.32, 0.20))
    elif look == 3:
        part(hair, (0, 1.50, -0.04), (0.52, 0.18, 0.48))
        part(hair, (0.02, 1.72, -0.06), 0.22)
    else:
        part(accent, (0, 1.56, 0.02), (0.54, 0.16, 0.52))
        part(accent, (0, 1.68, 0.02), (0.30, 0.16, 0.30))
        part(shade(accent, 0.75), (0.22, 1.54, 0.16), (0.16, 0.08, 0.16))

    part(EYE, (-0.11, 1.38, 0.22), (0.09, 0.10, 0.06))
    part(EYE, (0.11, 1.38, 0.22), (0.09, 0.10, 0.06))
    part(SHINE, (-0.08, 1.41, 0.25), 0.035)
    part(SHINE, (0.14, 1.41, 0.25), 0.035)
    part(BLUSH, (-0.18, 1.28, 0.20), (0.09, 0.05, 0.05))
    part(BLUSH, (0.18, 1.28, 0.20), (0.09, 0.05, 0.05))
    part((150, 72, 78), (0, 1.24, 0.22), (0.10, 0.035, 0.04))
