helllloooooo

this is kallen branch!

## Underscore proto (3D Ursina)

Modular god-view slice. First five minutes actually playable.


TO RUN THE GAME!!!!
```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m proto
```

### First 5 minutes
1. **Enter** — talk to **Mara** (E)
2. Stand on yellow **WORKSHOP** → **B** → **click** place → **T** → **Enter** stamp
3. Everyone else in the hall is optional

### Controls
| Key | |
| --- | --- |
| WASD | walk (camera-relative) |
| Arrows | pan the camera; in build, rotate |
| Drag | orbit. Build: right-drag (left click places) |
| Scroll | zoom |
| Mouse | Esc locks for clickless orbit |
| E / Enter | talk / continue / stamp |
| B | build on pad |
| Click | place part |
| Tab | cycle parts |
| T | test |
| Esc | leave build / unlock mouse |
| H | help |
| F5 | save |

### Layout
```
proto/
  app.py        bootstrap
  game.py       modes / input
  camera.py     god-view orbit / edge pan / hull cutaway
  player.py     walk
  world.py      maps + NPCs
  builder.py    pad build
  story.py      dialogue / zones
  state.py      flags / save
  ui.py         title + HUD
  visuals.py    Mac unlit shader
  config.py     colors / constants
```
