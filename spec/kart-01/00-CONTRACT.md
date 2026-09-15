# Stage 00 — Contract and Scene Safety

## Objective

Prepare an isolated Blender scene for exactly one low-poly game-prop go-kart named `Kart01`.

## Authorized initial cleanup

If and only if no user-created objects exist, remove Blender's default cube, camera, and light. If any other objects exist, stop as BLOCKED and list them; do not delete them.

## Required collections

- `KART01_ASSET`
- `KART01_PRESENTATION`

All asset geometry belongs in `KART01_ASSET`. Cameras, lights, and ground belong in `KART01_PRESENTATION`.

## File

Save immediately as `artifacts/blend/Kart01.blend`.

## Pass criteria

- Scene contains only authorized Kart01 collections and their contents.
- Units are Metric with unit scale `1.0`.
- Z is up; the ground plane is X/Y.
- The `.blend` file exists at the required path.

