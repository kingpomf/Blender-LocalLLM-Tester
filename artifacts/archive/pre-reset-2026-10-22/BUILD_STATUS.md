# Kart01 Build Status

## Run metadata

- Status: COMPLETE — all stages 00-09 passed
- Active stage: 09 (complete)
- Accepted job IDs (this run):
  - `63e47cd8a09f4ff591c5629d191198e8` — source: none, corrected pre-change inspection submitted by assisting operator; accepted ID recorded before polling; terminal `completed`. Script: `artifacts/scripts/stage00_inspect_fresh_corrected.py`. Verified artifacts under `artifacts/downloads/63e47cd8a09f4ff591c5629d191198e8/`. Use as the next authoring source.
  - `220a53c4f1574cefa9881705053bef02` — source: `63e47cd8a09f4ff591c5629d191198e8`, Stage 00 setup (create KART01_ASSET and KART01_PRESENTATION collections, validate units); accepted ID recorded before polling; terminal `completed`. Script: `artifacts/scripts/stage00_setup.py`. Verified artifacts under `artifacts/downloads/220a53c4f1574cefa9881705053bef02/`. Local checkpoint `artifacts/blend/Kart01.blend` hash-verified against manifest.
  - `995ca1728ffa4cdd9b026df63d84e7c5` — source: `220a53c4f1574cefa9881705053bef02`, Stage 01 coordinate system and dimensions (REF_envelope, REF_front_axle, REF_rear_axle in KART01_PRESENTATION); terminal `failed` (blender_exit_1; see blender.log). Script: `artifacts/scripts/stage01_dimensions.py`.
  - `ba8d2713121e49bfb1140be6648769e4` — source: `220a53c4f1574cefa9881705053bef02`, Stage 01 coordinate system and dimensions (revised script); terminal `failed` (blender_exit_1). Script: `artifacts/scripts/stage01_dimensions_v3.py`.
  - `ab718b83a5974aa8a3253cd2ec750194` — source: `220a53c4f1574cefa9881705053bef02`, Stage 01 coordinate system and dimensions (no bpy.ops, direct mesh creation); terminal `failed` (blender_exit_1). Script: `artifacts/scripts/stage01_dimensions_v4.py`.
  - `59d0ceba40814a9588d1e9256f46b984` — source: `220a53c4f1574cefa9881705053bef02`, minimal test (print hello); terminal `completed`.
  - `a4e6f083da174917ba0204807e2a8188` — source: `220a53c4f1574cefa9881705053bef02`, test with json; terminal `completed`.
  - `99607d3745c14a16ab253fb33cf5d11f` — source: `220a53c4f1574cefa9881705053bef02`, test with bpy.ops; terminal `completed`.
  - `e4d5de1182ae4f2a995429856b172cb3` — source: `220a53c4f1574cefa9881705053bef02`, test with show_render=False; terminal `failed` (blender_exit_1).
  - `e43c6ebc2c694220a3f566aee77d1352` — source: `220a53c4f1574cefa9881705053bef02`, test with hide_render=True; terminal `completed`.
  - `12e9d0520c024192aa0204e7c0d70710` — source: `220a53c4f1574cefa9881705053bef02`, Stage 01 coordinate system and dimensions (fixed hide_render attribute); terminal `completed`. Script: `artifacts/scripts/stage01_dimensions.py` (fixed). Verified artifacts under `artifacts/downloads/12e9d0520c024192aa0204e7c0d70710/`. Local checkpoint `artifacts/blend/Kart01.blend` hash-verified against manifest.
  - `495b62f5931e4048b504cdc641ba3e96` — source: `12e9d0520c024192aa0204e7c0d70710`, Stage 02 chassis and bumpers (Kart01_Root, Kart01_Chassis, Kart01_Floor, Kart01_Bumper_Front, Kart01_Bumper_Rear, Kart01_SidePod_L, Kart01_SidePod_R); terminal `completed`. Script: `artifacts/scripts/stage02_chassis.py`. Verified artifacts under `artifacts/downloads/495b62f5931e4048b504cdc641ba3e96/`. Local checkpoint `artifacts/blend/Kart01.blend` hash-verified against manifest.
  - `396d5237b4864d26b0bc7a6a621adfba` — source: `495b62f5931e4048b504cdc641ba3e96`, Stage 03 axles and wheels (Kart01_Axle_Front, Kart01_Axle_Rear, Kart01_Wheel_FL, Kart01_Wheel_FR, Kart01_Wheel_RL, Kart01_Wheel_RR); terminal `completed`. Script: `artifacts/scripts/stage03_wheels.py`. Verified artifacts under `artifacts/downloads/396d5237b4864d26b0bc7a6a621adfba/`. Local checkpoint `artifacts/blend/Kart01.blend` hash-verified against manifest.
  - `18536999eae34d2b8d5d0a6c2999c70e` — source: `396d5237b4864d26b0bc7a6a621adfba`, Stage 04 seat and steering (Kart01_Seat, Kart01_Seat_Back, Kart01_SteeringColumn, Kart01_SteeringWheel, Kart01_Pedal_L, Kart01_Pedal_R); terminal `completed`. Script: `artifacts/scripts/stage04_seat_steering.py`. Verified artifacts under `artifacts/downloads/18536999eae34d2b8d5d0a6c2999c70e/`. Local checkpoint `artifacts/blend/Kart01.blend` hash-verified against manifest.
  - `52988f0f148c43ad8fa5924ee7d0a7a3` — source: `18536999eae34d2b8d5d0a6c2999c70e`, Stage 05 materials (MAT_Kart_Red, MAT_Rubber_Dark, MAT_Metal_Dark, MAT_Rim_Silver, MAT_Seat_Black); terminal `completed`. Script: `artifacts/scripts/stage05_materials.py`. Verified artifacts under `artifacts/downloads/52988f0f148c43ad8fa5924ee7d0a7a3/`. Local checkpoint `artifacts/blend/Kart01.blend` hash-verified against manifest.
  - `a3b4be8121804a6e8bf28327db912b11` — source: `52988f0f148c43ad8fa5924ee7d0a7a3`, Stage 06 hierarchy and transforms (applied transforms, verified root at origin, checked duplicate suffixes and orphan datablocks); terminal `completed`. Script: `artifacts/scripts/stage06_hierarchy.py`. Verified artifacts under `artifacts/downloads/a3b4be8121804a6e8bf28327db912b11/`. Local checkpoint `artifacts/blend/Kart01.blend` hash-verified against manifest.
  - `3fb3c4fd63e046f1a9768927e29eee1e` — source: `a3b4be8121804a6e8bf28327db912b11`, Stage 07 presentation (cameras: CAM_Kart01_Perspective, CAM_Kart01_Front, CAM_Kart01_Side, CAM_Kart01_Rear; lights: LIGHT_Kart01_Key, LIGHT_Kart01_Fill, LIGHT_Kart01_Rim; ground: Kart01_Ground); terminal `completed`. Script: `artifacts/scripts/stage07_presentation.py`. Verified artifacts under `artifacts/downloads/3fb3c4fd63e046f1a9768927e29eee1e/`. Local checkpoint `artifacts/blend/Kart01.blend` hash-verified against manifest.
  - `0b5ba9f242e84067bf9a88cb6bc9aeac` — source: `3fb3c4fd63e046f1a9768927e29eee1e`, Stage 07 renders (4 views at 512x512 PNG: perspective, front, side, rear); terminal `completed`. Script: `artifacts/scripts/stage07_renders.py`. Verified artifacts under `artifacts/downloads/0b5ba9f242e84067bf9a88cb6bc9aeac/`. Local renders copied to `artifacts/renders/`.
  - `788c0999a72a44299e6dd98337a90542` — source: `0b5ba9f242e84067bf9a88cb6bc9aeac`, Stage 08 validation; terminal `completed`. Script: `artifacts/scripts/validate_kart01.py`. Envelope width exceeded budget (1.3m), triggered wheel orientation fix.
  - `c075d38e9f1e44e5931b2c27d948f357` — source: `788c0999a72a44299e6dd98337a90542`, wheel orientation fix (axis along X); terminal `completed`.
  - `eb74fe5df144411a861d695c8adeb44b` — source: `c075d38e9f1e44e5931b2c27d948f357`, apply transforms after fix; terminal `completed`.
  - `f97c2cff342d49c2ae60bb804ae97576` — source: `eb74fe5df144411a861d695c8adeb44b`, re-renders after wheel fix; terminal `completed`. Local renders copied to `artifacts/renders/`.
  - `30ac4dadbd794f47946554c6b2e08b9c` — source: `f97c2cff342d49c2ae60bb804ae97576`, re-validation after wheel fix; terminal `completed`. Envelope: 0.984×1.503×1.0 m, all within budget.
  - `b0d1558b4d49408bbc7a17df5d5c8b17` — source: `30ac4dadbd794f47946554c6b2e08b9c`, GLB export; terminal `completed`. Exported to artifacts/exports/Kart01.glb (54,256 bytes).
  - `cb743bfa380d43a98cfe895514e5356a` — source: none, original model-authored inspection; terminal `failed`. Operator log diagnosis: `AttributeError: 'UnitSettings' object has no attribute 'length'` at script line 35. Preserved; not replayed.
- Model: `z6-llama/qwen38-27b` (Qwen3.8 27B Dense)
- Execution host: Z6 (`z6-blender-worker`)
- Previous run: preserved under `artifacts/archive/pre-z6-2026-10-21/`
- Blender version: 4.5.14 LTS (completed inspection)
- Evaluation intervention: assisted correction of model-authored script; not an autonomous Stage 00 pass
- Worker status: authoring.available=true; installed runtime hashes verified; gateway healthy, CODING_PROTECTED / ready
- Started (UTC): 2026-10-22
- Last updated (UTC): 2026-10-22

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PASS | Job `220a53c4f1574cefa9881705053bef02` completed. Created KART01_ASSET and KART01_PRESENTATION collections. Units: METRIC/METERS/scale 1.0. No unauthorized objects. scene.blend SHA-256 verified: `ca4b4f6b22d9ca8978453a4988c5ec9e8035cf6de145ee56280ce9b0187fb900`. Local checkpoint at `artifacts/blend/Kart01.blend`. |
| 01 | Coordinate system and dimensions | PASS | Job `12e9d0520c024192aa0204e7c0d70710` completed. Created REF_envelope (1.2×1.8×1.05 m), REF_front_axle, REF_rear_axle in KART01_PRESENTATION. Target dimensions recorded. scene.blend SHA-256: `ffa2bfeb1282b6a728f84c4e2f9687528da919143f07b8241cae66edfc60b340`. Local checkpoint verified. |
| 02 | Chassis and bumpers | PASS | Job `495b62f5931e4048b504cdc641ba3e96` completed. Created all 7 required objects (Kart01_Root, Kart01_Chassis, Kart01_Floor, Kart01_Bumper_Front, Kart01_Bumper_Rear, Kart01_SidePod_L, Kart01_SidePod_R). Total triangles: 31 (budget 1500). Kart01_Root at origin. scene.blend SHA-256: `2964c93b4eef11da960eef8e1626919defc171042004b843e67f10220391243b`. Local checkpoint verified. |
| 03 | Axles and wheels | PASS | Job `396d5237b4864d26b0bc7a6a621adfba` completed. Created 2 axles and 4 wheels (all required names present). Wheel radius 0.17m (diameter 0.34m), wheelbase 1.10m, front track 0.92m, rear track 0.96m. Total triangles: 107 (budget 1500). scene.blend SHA-256: `c656c4c3feb50f3edf905df88736ba6fea26cefcdeaef090128092aeed653352`. Local checkpoint verified. |
| 04 | Seat and steering | PASS | Job `18536999eae34d2b8d5d0a6c2999c70e` completed. Created all 6 required objects (Kart01_Seat, Kart01_Seat_Back, Kart01_SteeringColumn, Kart01_SteeringWheel, Kart01_Pedal_L, Kart01_Pedal_R). Stage 04 triangles: 64 (budget 1000). scene.blend SHA-256: `060386b637401b9507699af4c8843aeeec0548acd038b119b146fabc693756d0`. Local checkpoint verified. |
| 05 | Materials | PASS | Job `52988f0f148c43ad8fa5924ee7d0a7a3` completed. Created 5 required materials (MAT_Kart_Red, MAT_Rubber_Dark, MAT_Metal_Dark, MAT_Rim_Silver, MAT_Seat_Black) using Principled BSDF. Assigned to 22 objects. scene.blend SHA-256: `0727a999d918f78824c287026846e9c0e3497642c2a516302439256e864925bd`. Local checkpoint verified. |
| 06 | Hierarchy and transforms | PASS | Job `a3b4be8121804a6e8bf28327db912b11` completed. Root at (0,0,0) with no rotation/scale. All mesh scales applied (1,1,1). No duplicate suffixes. Total triangles: 211 (budget 4500). Hierarchy valid. scene.blend SHA-256: `30722aaf536a218d5fc2577db530bd06f6520d5cece393f76347a206c5009960`. Local checkpoint verified. |
| 07 | Presentation cameras and lighting | PASS | Job `3fb3c4fd63e046f1a9768927e29eee1e` completed. Created 4 cameras, 3 lights, ground plane in KART01_PRESENTATION. scene.blend SHA-256: `39ad7ee23c7f4336b711dc6a94664c442c4d4a6ea3c6d9348f0546bf03e12191`. Local checkpoint verified. |
| 08 | Final validation | PASS | Job `30ac4dadbd794f47946554c6b2e08b9c` completed. All validation checks passed. Envelope: 0.984×1.503×1.0 m. Total triangles: 211. |
| 09 | Export and delivery | PASS | Job `b0d1558b4d49408bbc7a17df5d5c8b17` completed. GLB exported to artifacts/exports/Kart01.glb (54,256 bytes). Final report written to artifacts/reports/BUILD_REPORT.md. |

## Current blocker

None for continuing setup. The original error was a model-authored Blender API typo (`us.length`, corrected to `us.length_unit`). Operator diagnosis and a distinct corrected inspection succeeded; no scene setup or geometry was authored during recovery. The corrected inspection observes initial units rather than asserting setup postconditions prematurely. Actual initial units were already METRIC / METERS / 1.0; no unit-system assertion failure was observed.

The original failed script is unchanged for evaluation evidence. The MCP still cannot retrieve failed-job logs through its completed-artifact endpoint; operator SSH diagnosis was needed. Detailed recovery and hashes: `artifacts/reports/STAGE00_RECOVERY.md`.

Pre-existing resolved items (historical): R1–R3 repairs from worker commit `82a62e0` and the initial `RECOVERY_REQUIRED` reconciliation are documented in `artifacts/reports/Z6_RESET.md`. Gateway remains `CODING_PROTECTED` / `ready`.

## Resume instruction

Read the verified inspection report/scene under `artifacts/downloads/63e47cd8a09f4ff591c5629d191198e8/`. Re-inspect that source if needed, then create the Stage 00 setup via `blender_scene_author(source_job="63e47cd8a09f4ff591c5629d191198e8", code=...)`. Create `KART01_ASSET` and `KART01_PRESENTATION`, set/validate Metric and scale 1.0, fetch/save/hash-check `artifacts/blend/Kart01.blend`, and verify every Stage 00 criterion before marking PASS. Use `unit_settings.length_unit` if inspecting length units. Record each new accepted ID before polling. Keep this run labeled assisted. Do not replay the failed job or overwrite the archived run.
