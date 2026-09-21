# Proto backlog — original design → Ursina slice

Grounded in the Underscore game bible (academy → Earth → knowledge unlocks) vs what the proto already ships: god-view walk, pad builder, three maps, flag story, Pocket Build UI direction.

Ordered **small → significant**. Numbers are priority-ish within tier, not a strict build order.

**Shipped in proto (21–31, 42–45):** weld/confirm, break spans, stroke-to-beam, plate/wedge, sticky mix, circuit chain, spring lift, load meter, falling parts, blueprints, invention catalog, starter pick screen, XP bias unlocks, capstone starter-part gate, catalog node flash.

---

## Tiny polish (1–20)

1. Lower god-cam FOV toward 38–45 so islands read like table toys.
2. Facing-bake on meshes (+Y lighter, −Y darker) without leaving unlit.
3. Soft blob shadows under player, NPCs, trees, and placed parts.
4. Raise ambient / warm the key on Earth maps (craft-table noon).
5. Contact shadow under the ghost part while placing.
6. Pad floor as cake-slice tile (grass/dirt or steel lid) instead of flat glow planes.
7. Pad labels as screen chips matching name tags, not world banners.
8. Zoom % chip only in map mode (or hide under a threshold).
9. Sentence-case all remaining ALL CAPS HUD strings.
10. Build catalog remember last part/mat per pad.
11. Click catalog tile to select part (not only Tab).
12. Ghost part snaps to a soft grid on the pad.
13. Undo stack deeper than one delete (Ctrl+Z feel).
14. Confirm sound / stamp flash when Enter registers a build.
15. Distinct fail vs pass toast after T (collapse vs holds).
16. Day pip animates toward next day instead of jumping.
17. Sleep (Cot) advances day with a short fade, not instant flag fire.
18. Esc from talk does not skip critical flag-setting lines.
19. Help overlay lists current locked materials and why.
20. Title screen: Continue vs New Game (wipe save explicitly).

---

## Builder & physics toward the toy (21–40)

21. Weld / sticky as a real confirm step (parts become one island), not only crate cling.
22. Break force at joints — over-span collapses on T.
23. Stroke-to-beam: click-drag places a bar (chalk fantasy).
24. Plate / wedge primitives (bible base kit; proto has box/bar/ball).
25. Property mixing recipes (sticky-wood cladding on steel frame).
26. Circuits trial: battery → wire → switch → motor, not motor-only.
27. Hydraulics: pressure / spring taste, not only piston lift.
28. Structure: load test meter (how much the shelf holds).
29. Parts themselves can fall when unbraced (not crate-only dynamics).
30. Save pad blueprint; reload last build on re-enter.
31. Stamp writes a named invention into a simple catalog UI.
32. Ghost shows material color + weld highlights.
33. Motor direction / piston direction toggles.
34. Multi-crate or multi-goal pads (clinic door, shade span).
35. Free-build sandbox bay after capstone (no goal gate).
36. Placed Earth builds persist in the world, not just pad stamps.
37. Delete selected part under cursor, not only last placed.
38. Scale tool for bars (lengthen without new part type).
39. Hinge joint prototype (door / gate for storm clinic).
40. Stress tint (green→red) as optional later cosmetic on braces.

---

## Academy & people (41–60)

41. Name the player at New Game (Seeded teen rename).
42. Explicit starter pick screen after all three trials (not talk-to-mentor auto).
43. Starter XP bias: that branch’s next unlock is cheaper/easier.
44. Capstone must use a starter part (enforce the “specialized invention”).
45. Skill-tree node light-up UI when Sila registers a discovery.
46. Rio as full unselected-peer arc (resentment → optional reconciliation).
47. Cot / bunk as family/guardian with more beats than “Sleep.”
48. Jun as romance *seed* only (notice / gift), not completable in academy.
49. Mentors react differently after you pick another starter.
50. Optional NPC dialogue that does not advance the critical path (flavor flags).
51. Trust / heart values on key NPCs (even a 0–3 int).
52. Academy length pacing: soft gates so session feels 30–60 min, not 5.
53. Selection ceremony beat before elevator (short authored scene).
54. Goodbye line set that changes if you skipped optional talks.
55. Ship spaces stay visitable post-drop with mentors as lab contacts.
56. Peer/cohort NPCs who never deploy (society contrast).
57. Dialogue choices that set trajectory flags (`met_rio` style, expanded).
58. Yarn-like external dialogue files so Manasi can edit without Python.
59. Character want/fear one-liners in help or talk footer.
60. Photo / invention wall in the hall showing stamped builds.

---

## Earth loops & knowledge scarcity (61–80)

61. Colony vitality meters (shelter, water, power, morale).
62. Money sinks: buy specialist modules, gifts, contest entry, land plots.
63. Shop NPC who sells the starter branches you skipped.
64. Field sample scanner tool (find sticky / icy / bouncy in the wild).
65. Lab register UI that names the unlocked catalog node.
66. Travel rule UX: Colony A → Ship → Colony B only (block direct hops).
67. One-way flare from C2 is clear: cannot return until elevator done.
68. Elevator construction progress visible (day 1 / day 2 bar).
69. Storm clinic quest uses a hinged door + dust (real build-verb).
70. Shade tanks quest uses real roof span, not shelf-goal reuse.
71. Ravine bridge remains in the world after stamp.
72. Wild sample sites with silhouettes (latex vine, ice patch, wrecked rebar).
73. Colony 1 lead (Dust) trust gates a second job.
74. Pax “wrong mental model” tutorial beat that you gently correct by building.
75. Ivy / stay-on-ship trajectory flag after storm.
76. Day/night visual swap on Earth (navy fill + orange lamps).
77. Seasonal crisis stub: dust storm after icy unlock (already flagged — flesh it).
78. Colony services labels (hydro / metal / medicine / seed bank) as map identity.
79. Reputation banner when vitality crosses a threshold.
80. Second Earth discovery → lab → new tree node beyond sticky/icy/bouncy.

---

## Significant systems (81–100)

81. Full skill-tree screen (base + starter + field + deeper branches).
82. Practice XP: using a branch unlocks the next node faster.
83. Power graph v1 (battery, wire, switch powering motors/lights).
84. Vehicles as a use of the toy (simple cart / suspension), not a driving sim.
85. Horticulture / irrigation branch for Colony 2 shade → grow.
86. Climate sealing / medicine / optics as later tree branches.
87. Player-built tools: welder, fastener gun, flare, scanner.
88. Contests on the ship (whose bridge holds; named on elevator plaque).
89. Dating arc completion across ship returns (adventure-game romance).
90. Chapter aging (teen → twenties) on calendar + story flags.
91. Family comments on time away and what you built.
92. 3–5 more authored colonies with distinct biomes and services.
93. Listen-server 2-player co-op (shared world, per-player catalog/money).
94. Different starters in co-op as the party economy.
95. Host-controlled pause / calendar; clients follow.
96. Persistent shared builds and elevator state across sessions.
97. Colony vitality as the “take Earth back” campaign meter (no credits roll).
98. Infirmary knockout instead of soft fail / soft death.
99. Unity URP port with assemblies (Core / Player / Build / World / Story / Net).
100. Full Phase 1 vertical slice feel: ~45–60 min academy + Earth problem + lab return, with the knowledge loop named and obvious end-to-end.

---

## Already roughly in the proto (do not rebuild)

- God-view walk + orbit/zoom, hull cutaway
- Academy pads: workshop, hydro, circuit, structure, lab
- Starter mentors + stamp flags
- Elevator to Earth, ravine, sample → Sila sticky
- Colony 2 shade / pylon / 2-day elevator / flare
- Calendar day tick, money on stamps, F5 save
- Materials: wood, steel, sticky, icy, bouncy
- Pocket Build UI direction + cream loader

Use those as foundations; climb the list from polish into the bible’s missing spine (weld/confirm, skill tree UI, vitality, hub density, co-op).
