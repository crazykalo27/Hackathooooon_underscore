# Underscore log

- Proto rewritten into compartments: app, game, player, world, builder, story, state, ui, visuals.
- First-person movement (WASD + mouse) so you can actually walk the academy.
- Academy: only Mara is required; Rio and the rest are optional before the workshop.
- Mac black screen was Ursina's UI overlay (opaque without a 3.2 shader). Overlay off, lights on, hall is actually visible.
- Third-person camera sits in the academy: bunk, Mara, striped floor, pads; WASD walks the hall.
- Art: flat pastel geometry, open sky, stacked blocks — Monument Valley-ish, not a gray corridor.
- Characters are blocky Pixel Gun cuboids (limbs, face) still in flat pastel.
- Pads are plaza-sized; T runs gravity, stacking, pistons, motors, and gaps instead of teleporting the crate.
- Build mode leaves the player and orbits the pad: WASD turns around the center or zooms.
- Academy people cluster around bunk, table, and pad edges instead of a center line; names sit over their heads.
