# Stage 04 — Reusable bowling balls

Create `Ball_01`, `Ball_02`, `Ball_03`, each a separate movable mesh with a
distinct base color (blue, burgundy/red, green/teal). Provide a round, smooth
silhouette, diameter 0.216 m ±0.003, and three visibly recessed finger holes
arranged as a bowling grip on one hemisphere.

- Holes must be actual open recess geometry with inner walls and visible depth
  of at least 0.015 m. Painted black circles, floating black spheres and decals
  alone are insufficient. Closed blind sockets are acceptable.
- Pivot at sphere center within 0.001 m; applied scale (1,1,1). Radius is measured
  on the spherical exterior, excluding holes. No disconnected cutter objects in
  delivery; no unapplied Boolean dependencies.
- Maximum 8,000 evaluated triangles per ball. Materials portable to GLB with
  a clear color identity and a polished finish.
- Display all three balls supported on the shared return rack, with at least
  0.005 m separation between their exterior surfaces. No ball on a live lane in
  the final assembled scene. Orient grips so they are visible in the prop view.

Report bounds, pivot error, triangle counts, inter-ball distance, support contact
and measured hole depth/geometry. Export each ball separately centered at origin.
