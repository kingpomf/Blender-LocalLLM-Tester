# BowlingPair01 ball-generation and checkpoint diagnostic report

Operator-authorized reconciliation, 2026-10-24 UTC. No asset geometry or model-authored
script was repaired by this audit. It reopened the completed native scene, queried
the installed Blender API and preserved the original failure history.

## 1. What stopped the run

The tool ledger contains six failed authoring jobs: two during Stage00, one during
Stage01 and three during Stage04. The ball stage hit both old thresholds: three
failures from source `d1ce998472c349ac9f9fc2775afefdf6`, six across the trial.
Text-edit `oldString` failures were separate and did not consume this budget.

| Ball attempt | Actual terminal error |
|---|---|
| `a7ce66a8f47147f5a904cda1824ba8f6` | `KeyError: ... key "Clearcoat" not found` |
| `76e6ce714eec44f685da3329e41dffcc` | `ValueError: Empty or degenerate geometry: Ball_01` |
| `f1b81b3109f2428a880dba13fce45957` | `AttributeError: ... operator "extrude_face_only" doesn't exist` |

The fourth proposed submission used `extrude_region_unshared`, but was rejected
before execution. The model's final explanation incorrectly characterized all
three failures as extrusion problems and presented another unverified operator.

Exact submitted code is preserved in `testing/reconciliation-20261024/stage04-submission-01.py`
through `04.py` (04 was rejected, not executed). Recorded exceptions are in
`findings.json`. These snapshots differ from the active saved script in places;
failed edits do not prove a saved file matches the code actually submitted.

## 2. Installed API findings—not guesses

Read-only audit job **`4f572bf507534fe184d09d7014e0d60c`** ran on Blender5.2.3 LTS
from the existing completed source and reported:

| API | Available |
|---|---|
| `bmesh.ops.create_uvsphere` | yes |
| `bmesh.ops.extrude_discrete_faces` | yes |
| `bmesh.ops.extrude_face_region` | yes |
| `bmesh.ops.extrude_face_only` | **no** |
| `bmesh.ops.extrude_region_unshared` | **no** |

Principled inputs include **`Coat Weight`**, `Coat Roughness`, `Coat IOR`,
`Coat Tint` and `Coat Normal`; they do not include the legacy `Clearcoat` key.
The current saved ball script still calls the nonexistent `extrude_region_unshared`
at line67. Sending it unchanged will fail again.

Do not merely replace a function name while keeping an incompatible call/result
shape. `extrude_discrete_faces` accepts faces and returns a faces collection;
`extrude_face_region` works with geometry and returns geometry. Verify the actual
signature and operate on explicitly returned elements. Boolean sockets or directly
authored recessed topology are also permitted by the specification; it does not
require a particular BMesh extrusion method.

## 3. Geometry and validation defects in the ball code

1. **Degenerate extrusion risk:** attempt02 calls `extrude_discrete_faces` but ignores
   the return value, moving vertices only when `v.select` is set. BMesh selection
   is not a reliable identifier for newly extruded geometry. Coincident/unmoved
   side walls can have zero area. The worker rejects a mesh if **any face** has
   area below1e-12; that error does not necessarily mean the whole ball is empty.
   The manual UV grid also duplicates seam/pole positions. The failed log alone
   does not identify the exact offending face; validate all generated faces before
   linking the ball and do not silently weld away intended hole topology.
2. **Wrong API still in the proposed fix:** both `extrude_face_only` and the later
   `extrude_region_unshared` are absent. Use the runtime-confirmed APIs above.
3. **Surface separation is wrong:** centers are placed0.15m apart, while diameter
   is0.216m. Adjacent balls therefore overlap by about0.066m. The required0.005m
   surface gap needs at least **0.221m center-to-center** for equal-radius balls.
   Checking `center_distance < 0.005` does not test the required surface gap.
4. **Diameter tolerance is too loose:** code permits±0.006m, while Stage04 requires
   **0.216m ±0.003m**. The error message says±0.003 but the condition does not.
5. **Triangle accounting is incomplete:** call `calc_loop_triangles()` on each
   evaluated temporary mesh before counting; clear it afterward. Validate actual
   counts against8000, not a stale source-mesh cache.
6. **Hole acceptance is unmeasured:** `hole_depth=0.025` is only an intended value.
   Prove three distinct open recesses with inner walls and measured depth≥0.015m,
   a bowling-grip arrangement and no disconnected cutter geometry. Painted spots
   or translated coincident faces do not satisfy the contract.
7. **Support contact is not established:** there is no completed return rack yet.
   Positioning centers at radius+0.005 does not establish rack contact. Carry this
   as a measured dependency to Stage05 and revalidate before final delivery.

Pyright on the saved script reports six diagnostics. The nonexistent extrusion
operator is a confirmed runtime/API error. Optional node-tree and generic
NodeSocket typing diagnostics need correct guards/type narrowing; they do not
prove that valid typed socket `default_value` assignment is unavailable at runtime.

## 4. Earlier stage PASS claims also require repair

The integrity-verified repair base is **`d1ce998472c349ac9f9fc2775afefdf6`**, saved as
`artifacts/blend/BowlingPair01.blend`, SHA-256
`4480223492c6790eceb0e66729cd5e99b15ee8875c25c45cfeab76af521bd017`.
It is a completed, readable scene—not a claim that every stage in it passed.

- **Stage00 PASS:** actual metric units/scale1, five required collections, identity
  EMPTY root and visual meshes parented to it were verified.
- **Stage01 FAIL:**30 foul/arrow/dot objects sit around Z0.147–0.150 while lane tops
  are Z0.0; markings must remain within0.002m of the surface. Lane/approach primary
  extents are present and usable; repair them in place, not from an empty scene.
  Also inspect auxiliary ArrowStrip geometry. The audited lane/approach meshes
  have only4 faces; the saved make_box face list repeats the bottom/top faces in
  reverse order and omits two sides. Validate a complete, correctly oriented box
  topology rather than relying on bounds or `Mesh.validate()` to invent faces.
- **Stage02 FAIL:** both left gutters measure about0.410m wide rather than0.22–0.25m.
  Inner gutter sections extend onto playable lane surfaces; the left outer gutter
  reaches X=-1.8134, outside the specified pair envelope. Read the sampled sections
  in `native-audit.json`; correct side signs and adjacency, not just object names.
- **Stage03 FAIL:**18 non-head pins advance toward **-Y**, instead of+Y. All301
  faces of the shared pin mesh use the white slot—**zero red-band faces**. The mesh
  has26 boundary/nonmanifold edges, consistent with the skipped wraparound and
  incorrect bottom-cap indices. Counts20, height≈0.381, diameter≈0.121 and554
  triangles per pin are valid partial findings, not sufficient stage acceptance.
- **Stage04 FAIL:** no ball revision completed. Failed jobs cannot become sources.

Repair in order **01 → 02 → 03 → 04**, retaining the current scene and revalidating
dependent stages. Then proceed through05–09 only after actual checks pass.

## 5. Controlled continuation conditions

The operator approved **6 failures per source / 12 total**. All six historical
failures remain in the same guard database and same r2 queue. Initially this gives
three further failed attempts on the current source and six across the trial;
successful operator audits do not reset or consume failure counts.

Read this report, `CONTROLLED_CONTINUATION.md` and the relevant specifications.
Use the new explicit continuation command only after the preflight passes. Preserve
accepted IDs, run Pyright before authoring, read diagnostics after failures, and
update both ledgers with valid run statuses. Do not invent alternate APIs, weaken
measurements, reset state, select older sources to evade limits, or rebuild the
assignment from an empty scene. Stop on the new guard limit or uncertainty.
