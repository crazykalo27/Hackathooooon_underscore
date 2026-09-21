"""Blocky pastel figures — Pixel Gun cuboids, flat color."""

from __future__ import annotations

from proto.config import ACCENT, INK, PEACH, SHADOW
from proto.visuals import solid


def shade(col, k):
    return tuple(max(0, min(255, int(c * k))) for c in col[:3])


def attach(parent, shirt, skin=PEACH, pants=None, hair=None, accent=None, shoes=None):
    pants = pants or shade(shirt, 0.7)
    hair = hair or shade(shirt, 0.5)
    accent = accent or shirt
    shoes = shoes or INK

    def part(col, pos, scale):
        return solid(col, parent=parent, model="cube", position=pos, scale=scale, collider=None)

    part(SHADOW, (0, 0.02, 0), (0.62, 0.04, 0.42))
    # legs + shoes
    part(pants, (-0.11, 0.32, 0), (0.18, 0.62, 0.2))
    part(pants, (0.11, 0.32, 0), (0.18, 0.62, 0.2))
    part(shoes, (-0.11, 0.05, 0.05), (0.2, 0.1, 0.28))
    part(shoes, (0.11, 0.05, 0.05), (0.2, 0.1, 0.28))
    # torso + belt
    part(shirt, (0, 0.92, 0), (0.46, 0.52, 0.28))
    part(accent, (0, 0.66, 0.02), (0.48, 0.1, 0.3))
    # arms + hands
    part(shirt, (-0.32, 0.9, 0), (0.14, 0.5, 0.14))
    part(shirt, (0.32, 0.9, 0), (0.14, 0.5, 0.14))
    part(skin, (-0.32, 0.62, 0), (0.15, 0.12, 0.15))
    part(skin, (0.32, 0.62, 0), (0.15, 0.12, 0.15))
    # neck + big head
    part(skin, (0, 1.2, 0), (0.14, 0.1, 0.14))
    part(skin, (0, 1.46, 0), (0.42, 0.42, 0.42))
    part(hair, (0, 1.64, -0.03), (0.44, 0.16, 0.4))
    # face on local +Z
    part(INK, (-0.09, 1.48, 0.22), (0.08, 0.08, 0.05))
    part(INK, (0.09, 1.48, 0.22), (0.08, 0.08, 0.05))
    part((250, 242, 230), (-0.09, 1.47, 0.24), (0.04, 0.04, 0.03))
    part((250, 242, 230), (0.09, 1.47, 0.24), (0.04, 0.04, 0.03))
    part(ACCENT, (0, 1.34, 0.22), (0.12, 0.05, 0.04))
