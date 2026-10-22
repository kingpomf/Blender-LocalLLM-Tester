# Stage 03 — Reusable bowling pins

Create twenty individually movable pins named `Pin_L_01`..`Pin_L_10` and
`Pin_R_01`..`Pin_R_10`. All must share a reusable mesh or identical evaluated
geometry; each pin is one mesh object, not a joined rack.

- Height 0.381 m ±0.003; maximum body diameter 0.121 m ±0.003.
- Recognizable lathed ten-pin silhouette: flat base, broad lower belly, narrow
  neck, rounded head. Neck diameter must be less than 65% of maximum body diameter.
- White body and two red neck bands; material assignments or portable textures
  must survive export. Bands must not float outside or disconnect from the pin.
- Pivot is the base center; upright local +Z; object scale (1,1,1), rotation zero.
  Bases rest on Z=0 ±0.002 without visible intersections.
- Use standard numbered triangular racks, head pin #1 on each lane's center at
  Y=18.288. Rows have 1,2,3,4 pins, advancing +Y, nearest-neighbor spacing
  0.3048 m ±0.003; row separation is sqrt(3)/2 × 0.3048 m.
- Within each row number from left to right, starting at the head (#1; #2–3;
  #4–6; #7–10). Center every row on its lane.
- Maximum 2,500 evaluated triangles per pin.

Validate every actual pin's position, dimensions, pivot, count and geometry
budget. Save a reusable standalone pin at origin during export, without moving
the assembled rack in the final native scene.
