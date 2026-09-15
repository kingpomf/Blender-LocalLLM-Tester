# Stage 06 — Hierarchy and Transforms

## Hierarchy

Parent every asset object directly or indirectly to `Kart01_Root`. Presentation objects must not be children of `Kart01_Root`.

## Transform rules

- `Kart01_Root` location `(0, 0, 0)`, rotation `(0, 0, 0)`, scale `(1, 1, 1)`.
- Apply scale on every mesh object; evaluated scale must be `(1, 1, 1)` within `0.001`.
- Apply rotation where safe. Wheel meshes may retain an intentional local rotation only if their local X axis is documented as the spin axis.
- No object name may end in Blender duplicate suffixes such as `.001`.
- No orphan mesh or material datablocks created by this build may remain.

## Total budget

Complete Kart01 asset: `<= 4,500` evaluated triangles.

