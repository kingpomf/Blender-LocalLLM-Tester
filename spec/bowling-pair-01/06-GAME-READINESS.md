# Stage 06 — Materials, hierarchy and collision

## Visual assets

- Root `BowlingPair01_ROOT` at origin, identity rotation/scale. Static sections,
  pins and balls remain separately addressable descendants. Pins and balls must
  not be joined to lanes or each other. Use the collections defined in Stage 00.
- All visual mesh scales (1,1,1), no negative scales, no unapplied topology
  modifiers. Preserve the specified pin and ball pivots; static piece origins
  should be documented and useful for placement, not distant arbitrary points.
- Nondegenerate faces, finite coordinates, outward exterior normals, no loose
  cutter objects. Intentional gutter/open architecture boundaries are allowed.
- Maximum 150,000 evaluated visual triangles for the whole pair, counting every
  placed instance. Excludes presentation and collision. Record per-category and
  total counts; linked instances still count twenty times for twenty pins.
- At least wood, white pin, red stripe, three ball colors, gutter/metal, seat and
  screen material identities. Use Principled-compatible PBR values. Required
  visual features must export as material assignments or embedded textures;
  Blender-only procedural nodes are not sufficient. Use simple UVs for surfaces
  with textures; embed all textures in GLBs and pack them into the native scene.

## Collision deliverable

Create named low-complexity static proxies in `BP01_COLLISION`, all prefixed
`COL_`, excluded from beauty renders and visual exports. Minimum: two lane beds,
four concave gutter troughs (piecewise convex strips acceptable), outer rails and
rear catch stops. Tops and boundaries align with visual playable surfaces within
0.01 m. Gutters must not become flat bridges over the trough. No proxy crossing
the central playable path above the lane plane. Collision total <=10,000 triangles.

Document dynamic collider recommendations: centered sphere radius 0.108 m for
balls; compound convex approximation for pins, with base-pivot offset explained.
No requirement to implement or tune a physics engine. Collision proxies are a
separate export, with original placement relative to the pair origin.
