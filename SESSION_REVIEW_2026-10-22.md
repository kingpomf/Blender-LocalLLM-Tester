# Review of stuck 100K session

Session: `ses_e9c18d959ffem6YPRJCfSlIb7w`. Reviewed during the separately authorized
256K context upgrade. Original scripts, checkpoints, renders, and stage claims were
not overwritten or marked passed by this review. No repaired Kart01 scene was built.

## Verdict

This is an API/context-handling and validation/recovery failure, not an exhausted
context window. The diagnostics tool is working: it repeatedly returns the exact
exception. The agent did not use that evidence to make a relevant code change,
did not respect its repair budget, and accepted unsupported stage claims.

### 1. Repeated identical failed submissions

Read-only inspection of the CPU worker database confirms **11** sampled validation
jobs used the same source `af5a5f32725047799da134617e2841bc` and the exact same code
SHA-256 `379a18ae6d76a4c4ecf3e99a62a9f3b4c519dcc2ab229b297c86267ce9c572ae`:

`074e43a86fb442049b5fca4abbe98114`, `903c6c5ebd7c4d518421131c9f915d64`,
`842fe2771663416d9847483ec8a0846f`, `e89a78c080454c849a7499408911228a`,
`e107395ed83c40159a02a0e286aad7cf`, `4349762b63614247b841a42dc319c51e`,
`970c1e1743dc4347ab57b93b54cfb5ac`, `409f86c45a104260a1daa2613c816d0b`,
`b96e728e1b4e4a65b39522ccc92cc6da`, `de01a92d7e0c433a8923745c04071fe7`,
and `ce2dbd205e12450fa3ffa3634f5fdd62`.

All were terminal failed jobs. Saying "try a different approach" did not change
the submitted program. This exceeds the documented bounded-repair policy.

### 2. Active-object assignment was never correctly repaired

The correct writable property is `bpy.context.view_layer.objects.active = obj`.
`scene.active_object` and `view_layer.active_object` are invalid; the context's
`active_object` property is read-only. `bpy.ops.object.select_set` does not exist;
selection is an Object method, `obj.select_set(True)`. Selection alone does not
make a mesh active. The Edit-mode error is consistent with an unsuitable active
object/context, not a missing Edit mode in Blender 4.5.

More fundamentally, a validator should not need those operations: reading scales
and measuring evaluated loop triangles avoids context-sensitive Edit mode and
does not silently modify the asset under test.

API references: [LayerObjects.active](https://docs.blender.org/api/4.5/bpy.types.LayerObjects.html#bpy.types.LayerObjects.active),
[Object.select_set](https://docs.blender.org/api/4.5/bpy.types.Object.html#bpy.types.Object.select_set),
[Mesh.calc_loop_triangles](https://docs.blender.org/api/4.5/bpy.types.Mesh.html#bpy.types.Mesh.calc_loop_triangles).

### 3. Four labels, one rendered camera

Actual authored `scene.json` has `active_camera: null`. All four named cameras
have zero rotation; none is explicitly aimed at the kart. The render job's actual
scene instead has `active_camera: "Camera"`, the renderer's generic fallback.

The following downloaded PNGs have **identical decoded RGBA pixels**:
`b869a1133c40499ba2546ffee3b0ed41`, `3dcba244dee844a9ba2673e92563c96d`,
`b1b919a0653a4d0cbc567dc027899791`, `f476c126a599408e95ded74d72591a9f`.
Their decoded-pixel SHA-256 is
`4799da60e151621f483510bae668999f3bf20e81bd731e72fbbcb49fc0a08e09`.
Different PNG file hashes did not establish different views. Direct image review
shows a small kart-like assembly from a generic view, not four specified views.

The active `artifacts/renders/` directory contains no PNGs, despite the Stage 07
ledger claiming the four files were saved there. Stage 07 PASS is unsupported.
`blender_scene_modify` correctly rejected a camera because that interface edits
meshes only. Select/aim cameras using authoring revisions or camera markers.

### 4. Validator correctness is substantially incomplete

The submitted script counts the four names in its own required-name list rather
than counting actual scene wheels. It explicitly assumes envelope/ground contact,
wheelbase/tracks, duplicates, and collection checks pass. It declares required
materials/cameras/lights but never validates them. It tries to fix transforms
while claiming to measure them, and triangulates original meshes in Edit mode
rather than inspecting evaluated geometry. Ground is incorrectly included among
objects that must be parented to the asset root.

It initially refers to a Mac-only script at `/job/validate_kart01.py`, which was
never uploaded; it then checks Mac-relative render paths inside the worker, uses
wrong delivery filenames, and attempts to assign the read-only `bpy.data.filepath`.
Removing the immediate exception would not make this a valid Stage 08 checker.

Earlier claims also need review: the saved wheel dimensions are approximately
X/Y/Z `0.34 / 0.34 / 0.14 m` (thickness along Z rather than required X); axles are
longest along Z. The saved scene contains `Cube.001`–`.005`, and the floor and
ground have no materials. This is not just a final-validation syntax problem.

### 5. Handoff and compaction preserve unsupported conclusions

BUILD_STATUS.md still says NOT_STARTED/no active source/no accepted jobs, while its
table claims Stages 00–07 PASS and HANDOFF.md claims Stage 07 verified. The read-only
resume preflight currently fails on these contradictions. The transcript does not
show the agent resolving that failure. This preflight is an explicit workflow
step, not an enforcement hook that automatically intercepts every tool call.

Compaction summaries assert that four views rendered and stages fully passed,
despite the camera and artifact evidence above, and describe an already-completed
render as pending. A longer context can reduce compaction frequency but cannot
make these conclusions true or stop an unchanged-code retry loop.

## Recovery recommendation

Stop the retry loop. Reconcile ledger/handoff from actual jobs and artifacts;
revalidate the earliest affected requirements before treating any source as
verified. Repair cameras/geometry/materials in focused revisions, with named
camera selection and framing checks. Build a measurement-only validator covering
every Stage 08 requirement and a separate local delivery check. Require failed
checks to produce FAIL, with no placeholders. Keep the original attempt as
evaluation evidence and label any external repair as assisted.
