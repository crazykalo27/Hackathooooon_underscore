helllloooooo

this is kallen branch!

## Underscore proto (3D Ursina)

Modular first-person slice. First five minutes actually playable.

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m proto
```

### First 5 minutes
1. **Enter** — Mara talks
2. **WASD** walk the hall → **E** on Rio  
3. Stand on yellow **WORKSHOP** → **B** → **click** place → **T** → **Enter** stamp

### Controls
| Key | |
| --- | --- |
| WASD | move |
| Mouse | look (Esc unlocks) |
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
  player.py     first-person move
  world.py      maps + NPCs
  builder.py    pad build
  story.py      dialogue / zones
  state.py      flags / save
  ui.py         title + HUD
  visuals.py    Mac unlit shader
  config.py     colors / constants
```
