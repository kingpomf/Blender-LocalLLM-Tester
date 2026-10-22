# Stage 01 — Lane pair and markings

## Layout in meters

| Feature | Required value | Tolerance |
| --- | --- | --- |
| Lane surface width | 1.0668 | ±0.005 |
| Foul line to head-pin center | 18.288 | ±0.01 |
| Lane center X | -0.95 and +0.95 | ±0.005 |
| Surface Z | 0.0 | ±0.002 |
| Approach length behind foul line | 4.572 | ±0.01 |
| Lane surface end Y | 19.20 | ±0.01 |

Create `Lane_L_Surface`, `Lane_R_Surface`, `Approach_L`, `Approach_R`.
Lane surfaces span Y=0 to 19.20; approaches span Y=-4.572 to 0. Geometry has
thickness below Z=0. Separate pin-deck pieces may overlay the rear region with no
z-fighting. The pair's outer playable/gutter width must fit within X=-1.80..1.80.

Add a visible dark foul-line strip per lane at Y=0 (0.02–0.05 m wide),
seven targeting arrows per lane centered near Y=4.57 (±0.10 m), and seven
approach dots per lane near Y=-1.0 (±0.10 m). Keep markings flat to the surface
within 0.002 m. Wood-board variation must read along Y. Flat color bands or
portable baked textures are acceptable. Measure world-space bounds, spacing,
surface height and the actual marking count; do not pass intended constants.
