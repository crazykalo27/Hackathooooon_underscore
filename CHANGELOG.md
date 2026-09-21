# Underscore log

- Names are screen labels now (no black world boxes). Loader paints for real while the hall builds in slices.

- Pad reset moved to X (and an X RESET tray button) because R is rotate.

- Name tags sit above people, stay upright, turn with the camera, and scale so they stay readable.

- Build: R spins the held part 90 degrees, F tips it onto the axis R cannot reach.

- UI type is Pixelify Sans, larger and less crunchy than the 5-pixel face.

- Arrow keys pan the god-view; in build they orbit the pad.
- Hull and UI shifted off brass/iron to void navy, cyan trim, and ice lights.
- HUD, talk, and build text sit on iron/brass plates with a pixel font — no more overlapping labels or floating type.
- Build uses that same camera — no more hull-clamped pad orbit.
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
- Ship hall is a hull now: steel-framed windows look out on starry space, not an open pastel sky.
- Hull is wider and taller; build cam starts close, stays inside the ship, scroll tilts up/down.
- Pad tests: the crate sits where it will fall; stacked parts hold it instead of getting shoved.
- Build tray is a little pixel hull terminal: brackets, pips, and a blinking link light.
- Ship interior is a darker steampunk hull: iron plates, brass rivets, pipes, lamps — not a pastel room.
