# Stage 00 — Contract and scene safety

## Goal

Create `BowlingPair01`: a cohesive, modular two-lane ten-pin bowling alley asset
kit for a potential future game. Aim for clean low/mid-poly stylized realism.
The local agent must author original geometry using Blender Python; no imported
asset packs, downloaded meshes, or historical kart starting scenes. Procedural
materials are allowed, but required appearance must survive GLB export.

## Required scene foundation

- First complete `REFERENCE_IMAGES.md`: generate three concept references with imageMCP, download/hash them, and write `artifacts/references/DESIGN_GUIDE.md`. `python3 scripts/check_references.py` must pass before any Blender authoring. Use the design guide for forms/materials/composition; the written dimensions, counts and acceptance requirements override generated-image errors. Record visual-inspection limitations honestly.
- Start with the worker's isolated zero-object scene, without source_job.
- Metric units, unit scale 1, meters; Blender X/Y ground plane, Z up.
- Origin: midway between lanes at the foul line, at the lane surface height.
  Positive Y points toward the pins; positive X is right viewed from approach.
- Create collections `BP01_STATIC`, `BP01_PINS`, `BP01_BALLS`,
  `BP01_COLLISION`, `BP01_PRESENTATION` and empty root `BowlingPair01_ROOT`.
- All exported visual objects descend from that identity-transform root.
  Presentation cameras/lights and collision-only objects must be separate.
- Use stable, unique names and save scripts under `artifacts/scripts/`.

Read all stages before geometry work. Report actual collections, units, axes and
root transforms. Save the native checkpoint. This stage is setup, not a claim
that geometry exists. Game code, physics simulation, animation and a pinsetter
mechanism are not required. Extra decoration is allowed within the budget and
must not obstruct playable lane surfaces or obscure required evidence.
