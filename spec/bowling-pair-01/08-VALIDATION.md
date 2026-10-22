# Stage 08 — Final measured validation

Save a reproducible read-only Blender validation script in
`artifacts/scripts/validate_bowling_pair01.py` and machine-readable output at
`artifacts/reports/validation.json`. Validation measures the final saved scene;
it must not apply transforms, reposition objects or repair geometry while testing.

Include each required criterion from Stages 00–07 with ID, expected value/range,
observed value, tolerance/unit, PASS/FAIL and object names. Include:

- Actual units/root/collection membership, lane bounds/centers/surface heights,
  approaches, markings, gutter profiles, pit/deck dimensions and clearances.
- Twenty distinct pin objects, numbered rack coordinates, nearest-neighbor
  spacing, dimensions, silhouette/neck ratio, base pivots and surface contact.
- Three ball objects, diameters/center pivots, actual finger-hole depth/topology,
  supported placement and non-overlap.
- Required dressing, labels, materials, transforms, evaluated triangle budgets,
  degenerate-face/normal checks and collision alignment/coverage/exclusion.
- Camera selection and framing, actual render job IDs and file paths. Delivery
  hashes/GLB round-trip checks may be appended after Stage 09.

Do not use existence, comments, expected-value arrays or unconditional true as
proof of measured geometry. Separate measured checks from qualitative visual
review. If a requirement cannot be measured, supply explicit inspection evidence
or mark it unresolved. A failed required check keeps the build FAIL. After a
repair, rerun affected geometry checks, exports and relevant renders so evidence
and delivery describe the same final revision.
