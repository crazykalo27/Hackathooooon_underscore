# Pocket Build look — how they get it, how we copy it

MoonBear’s *Pocket Build* (2017, Jaynesh Vekaria; PC twin is *SUPER BUILD*) is a toy-table diorama, not a world you stand inside. The camera looks down on a collection of painted miniatures sitting in empty sky. That one framing decision does more than any shader.

Official store art pushes this further into clean isometric low-poly (pastel windmills, Tudor houses, empty beige ground). Player worlds use a bigger mixed-artist catalog and get denser. **Copy the system, not every prop.** The system is: island in a void, cake-slice land, catalog objects, bright fill light, simple materials, readable silhouettes.

Not Minecraft (voxels). Not Townscaper (merged blobs). Not Monument Valley (impossible architecture). Closest cousins: Playmobil on a table, *The Battle of Polytopia*, *Islanders*, *Godus* land tiles.

---

## The eight moves

1. **Void, not planet.** The map is an island (or a few) in a flat colored sky. No horizon, no textured skybox, no distant mountains. Negative space is the frame.
2. **Cake-slice terrain.** Land is a chunk: grass cap, dirt/rock sides, flat enough to place toys on. Stack chunks to make cliffs. Water is a bright turquoise slab, often translucent.
3. **Catalog, not kit.** You place whole objects (a house, a tree, a person, a barrel). Complexity comes from stacking and clutter, not from high-poly meshes.
4. **Bright fill, soft key.** High ambient so nothing goes black. One warm sun for form. Shadows are soft contact blobs, not hard drama.
5. **Painted plastic, not PBR.** Albedo color + a bit of facing shade. No roughness maps, no reflections, no photoreal textures. Faces read as toys.
6. **Chunky silhouettes.** Roofs, towers, lollipop/blob trees, thick fences. You should recognize a house at 200m zoom.
7. **Toy scale.** People are small vs buildings. Trees, giants, and props do not share one real-world scale. That inconsistency is the charm.
8. **Decorate until it feels collected.** Paths, fences, flowers, lanterns, animals. Empty grass looks like a prototype. Dense clutter looks like Pocket Build.

---

## Palette

Stay in the pastel-but-saturated band. Whites are warm cream, greens are yellow-green, water is candy turquoise, sky is clear baby blue. Avoid grey-brown realism and neon.

| Role | Hex-ish RGB | Notes |
| --- | --- | --- |
| Sky void (day) | `168, 214, 255` → `186, 224, 255` | Flat or a very slight top-to-horizon fade. No clouds required. |
| Sky void (night) | `18, 28, 72` | Deep blue, not black. |
| Grass cap | `168, 204, 88` / `196, 214, 96` | Yellow-green, like a model-rail mat. |
| Dirt side | `196, 148, 96` | Exposed cake edge. |
| Cliff / rock | `180, 168, 148` | Warm stone, not granite grey. |
| Sand | `236, 210, 140` | Desert tiles. |
| Snow | `236, 244, 252` | Soft, not ice-blue. |
| Water | `96, 196, 214` at ~50–70% alpha | Bright, shallow, toy pool. |
| Wood | `196, 140, 88` | Warm, even. |
| Plaster / castle | `236, 230, 214` | Cream, not white. |
| Roof clay | `196, 92, 72` | |
| Roof slate / turret | `72, 120, 176` | The classic Pocket Build blue cone. |
| Gold trim | `232, 188, 72` | Used sparingly. |
| Night lamp | `255, 176, 72` | Emissive. Windows and lanterns only. |
| Skin | `236, 196, 168` | |
| Shadow blob | `20, 28, 40` at ~20% | Under every object. |

Rule: if a color looks like a photograph, desaturate the brown and push it toward candy.

---

## Lighting

Pocket Build reads as “noon on a craft table.”

**Day**
- Ambient: high, slightly cool — about `(180, 196, 214)`. Fill should be ~60–70% of the key so shade is still a color, not a hole.
- Key: warm white `(255, 236, 210)`, elevation ~40–50°, slightly to the side. One sun. No second rim unless night.
- Shadows: soft, short, low contrast. Contact blob under each object matters more than a crisp shadow map.
- Fog: none, or a whisper. The void is already the fade.

**Night**
- Global swap, not a slow atmospheric sim. Ambient drops to navy. Key becomes dim moonlight `(140, 170, 220)`.
- Warm emissives punch: windows, lamps, campfires. That warm/cool split is the whole night look.

**How they fake form without PBR**
Most mobile toys do not light every pixel. They bake facing:
- Top face: +15–25% lighter
- Sun-facing side: base
- Opposite side: −15–25%
- Underside: −35%

Our proto’s shader is unlit color (`proto/visuals.py`). That is fine. Do **not** switch to full PBR. Add either (a) that facing bake when we spawn a mesh, or (b) a tiny Lambert term in the existing GLSL 150 shader. Same toy read, still Mac-safe.

---

## Camera

The hero shot is 3/4 god-view. The world should look like a model you could pick up.

| Knob | Pocket Build | Our proto now | Copy |
| --- | --- | --- | --- |
| Feel | Near-isometric, slight perspective | Perspective FOV 52 | Drop FOV toward 38–45, or orthographic |
| Pitch | ~35–45° | 38° | Keep. Do not go cinematic-low. |
| Yaw | Free orbit | 42° start | Fine. |
| Background | Flat sky color | Sky color already | Keep void. No starfield on earth maps. |
| Zoom | Table → dollhouse → first person | 4–400 | Same idea. Distant zoom must still read silhouettes. |

No motion blur, no film grain, no chromatic aberration. The image should look like a product shot of toys.

---

## Terrain

Land is the stage, not the scenery.

- **Chunk, not heightmap.** A tile is a box or a rounded slab: thin grass lid, thicker dirt body.
- **Sides always show.** That dirt ring is how the brain says “miniature,” same as a wedding-cake layer.
- **Biomes are swaps of the lid color** (grass / sand / snow / stone), not new mesh language.
- **Water is another slab**, slightly inset, brighter than real water, optional transparency. No reflections.
- **Islands float.** A little air under the chunk, or a ring of water, then void. Do not bury the map in a continuous ground plane that goes to the horizon.
- **Stacking is the sculpting tool.** Cliffs = two or three cake slices. Paths = darker/lighter decals or thin slabs on the lid.

---

## Models and silhouettes

Meshes stay medium-low. Detail is a few extra boxes, not displacement.

**Buildings**
- Big roof, short walls. Roof color is the ID.
- Chimneys, timber frames, arched doors as separate chunks, not texture.
- Castles: cream mass + blue cones + gold dots. Windows are dark insets, not glass.
- One building is a complete object. A city is many of them, not a modular wall kit (unless the player is assembling).

**Trees**
- Trunk cylinder + 1–3 canopy blobs (sphere / low ico / stacked cubes).
- Canopy slightly yellow-green. A few autumn oranges in the same scene is fine.
- Scale: shorter than a two-storey house, taller than a person.

**Props**
- Barrels, fences, lanterns, crates, flowers, carts. Each is 1–4 primitives.
- Place them in groups. Three barrels beat one.

**Characters / animals**
- Chibi: big head, short legs, two-dot face. We already do this in `proto/figure.py`.
- Recolor shirt/hair, do not add realism.
- People are markers of life, not the visual subject. They should be readable dots from the god camera.
- Animals a bit oversized. Giants exist on purpose.

**Scale law:** if it looks “correct” like architecture photography, enlarge the roofs and shrink the people.

---

## Materials

One material language for the whole catalog:

- Unlit or Lambert. Vertex / face color carries the identity.
- Optional soft AO in creases (where roof meets wall, under canopy).
- Specular: none, or a 2% plastic sheen. Never wet stone.
- Texture, if any: a flat painted albedo. No normal maps.
- Emissive only for lamps and night windows.

Our current `solid()` path (flat `p3d_ColorScale`) already matches this if we stop painting everything navy/steel and start painting cream / grass / wood.

---

## Composition

A Pocket Build screenshot is usually:

1. One island or castle cluster
2. Lots of sky around it
3. A few trees as scale ticks
4. A path or fence that leads the eye
5. Tiny figures so you feel like a giant

Density curve: **empty void, decorated lid.** Do not scatter props into the sky. Do not leave the lid bare.

Hero angles: slightly below a tall build (toy monument), or high 3/4 over a village (model railway). Both assume the void.

---

## UI

Copied in `proto/ui.py` and `proto/loading.py`:

- Slim navy top bar: peach pip + world name, gold coins, green day, roof-blue help chip
- Cream cake-slice cards for objective, banner, talk, help, and the build catalog
- Build catalog is a tile grid with toy glyphs, not a terminal parts list
- Sentence case, no rivets / LEDs / "SEEDED"
- Loader is a cream card on sky void, pastel bouncing pips

---

## What we already have vs what to change

| Piece | Now | Pocket Build copy |
| --- | --- | --- |
| Shader | Unlit color, Mac-safe | Keep. Add facing bake or 1-light Lambert. |
| Camera | God orbit, FOV 52 | Lower FOV; keep pitch. |
| Figures | Blocky chibi | Keep. They already fit. |
| World | Cream toy rocket, cake-slice colonies, chibi crew | Shell opens on the camera side of the player. |
| Lights | Cool, dim ambient `(72,104,148)` | Raise fill; warm the key. |
| Materials | Navy, cyan, brass | Grass, dirt, wood, cream, clay roof. |
| Ground | Continuous hall / hull | Cake-slice pads and islands. |
| Shadows | Barely there | Blob under every placed thing. |

The ship-interior look (void navy, ice lights) is a different show. Pocket Build is the **outdoor toy map**. Do not mix them in one room.

---

## Copy recipe (do this, in order)

1. **Void sky.** `window.color` = day blue `(176, 216, 248)`. Fog off.
2. **Lights.** Ambient `(184, 200, 216)`, sun `(255, 236, 214)` at ~45° pitch. Night = navy fill + orange lamps.
3. **Cake tile.** Box: top `GRASS`, sides `DIRT`, maybe a darker underside. Scale like a table tile, not a continent.
4. **Facing bake.** When spawning a mesh, lighten +Y faces, darken −Y. Instant toy form on the unlit shader.
5. **Blob shadow.** Thin dark ellipse under player, NPCs, buildings, trees.
6. **Catalog props.** House = cream box + clay roof wedge + dark door inset. Tree = brown stick + 1–2 green spheres. Fence = posts + rail. Stop there.
7. **Clutter pass.** Three props around every building. A path slab. Two trees as bookends.
8. **Camera.** FOV 42, pitch 40°, pull back until the island sits in sky like a product shot.
9. **No PBR, no outlines, no textured skybox.** If a change makes it look “more real,” undo it.

---

## Sources

- MoonBear store pages and *SUPER BUILD* Steam stills: the clean isometric marketing language (pastel islands, Tudor set, western ranch, night standing stones).
- Play listing tags: stylized sandbox, free orbit camera, first-person walkthrough as a second view.
- `r/pocketbuild` player worlds (castles, fairy villages, Hogwarts-scale stacks): same void + lighting, denser catalog composition.
- Dev framing (Jaynesh): “Lego for your phone,” no timers, no economy — the visuals serve calm collecting, not simulation grit.

If a reference fights the eight moves (photoreal grass, dark contrast, continuous horizon), it is not the look.
