# Kart01 Build Status

## Fresh test — 100K context and durable-handoff reset, 2026-10-22

- Status: NOT_STARTED
- Next stage: 00 — Contract and scene safety
- Active source job: none
- Accepted job IDs: none for this run
- Default model: `z6-llama/qwen38-blender-35b` — Qwen3.8 35B A3B Blender v1, 262,144-token context; the operator may select another configured model before `/kart-start`.
- Actual model used: not yet recorded
- Execution host: Z6 (`z6-blender-worker`)
- Operator intervention: none in this run
- Active outputs: cleared; no previous PASS is reused

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PASS | Job `5a1ae782950b459dbc0d497d9e61e5aa` completed; scene.json shows KART01_ASSET and KART01_PRESENTATION collections, METRIC units scale 1.0; blend at `artifacts/blend/Kart01.blend` (sha256 `17e82db0c40197c3de3f0768de86add661cb7e2dcbe09d3bcde600fb59ff232b`) |
| 01 | Coordinate system and dimensions | PASS | Job `e5aba61a71c640f8a7de88d87a946047` completed; 7 reference guards created (REF_Ground_Z0, REF_X_Width, REF_Y_Length, REF_Z_Height, REF_Wheelbase, REF_FrontTrack, REF_RearTrack) with envelope dimensions; blend at `artifacts/blend/Kart01.blend` (sha256 `e403eb1f5716f3094bca18949d494ede44b4abd249241b72520fd05046043f97`) |
| 02 | Chassis and bumpers | PASS | Job `33fc10aca7224bc092f54419822f0918` completed; 7 asset objects created (Kart01_Root, Kart01_Chassis, Kart01_Floor, Kart01_Bumper_Front, Kart01_Bumper_Rear, Kart01_SidePod_L, Kart01_SidePod_R); blend at `artifacts/blend/Kart01.blend` (sha256 `040f14687780f04721d0471f4a9b7d2ef2dd6092465e37fe0ec253e3f2c5b263`) |
| 03 | Axles and wheels | PASS | Job `e725df6eef144a38a04c1db61f0cb2b9` completed; 4 wheels + 2 axles created (Kart01_Wheel_FL, Kart01_Wheel_FR, Kart01_Wheel_RL, Kart01_Wheel_RR, Kart01_Axle_Front, Kart01_Axle_Rear); blend at `artifacts/blend/Kart01.blend` (sha256 `31b6662c366814f15d7cc46cf5d9fe83e9a229fef89e857dba4144ffdb98878f`) |
| 04 | Seat and steering | PASS | Job `03da488ace634b6dbd4ce9681480771e` completed; 5 seat/steering objects created (Kart01_Seat, Kart01_SteeringColumn, Kart01_SteeringWheel, Kart01_Pedal_L, Kart01_Pedal_R); blend at `artifacts/blend/Kart01.blend` (sha256 `44693ea3416844eabe57f1df1ebc90651805d26489fa9502f1df2ecca57ecb01`) |
| 05 | Materials | PASS | Job `384440ff947445c8b8628ea494eeb8b5` completed; 5 materials created (MAT_Kart_Red, MAT_Rubber_Dark, MAT_Metal_Dark, MAT_Rim_Silver, MAT_Seat_Black) and assigned to mesh objects; blend at `artifacts/blend/Kart01.blend` (sha256 `ef6be6924814bda33630141d442b01c18bc8d06b24d387420b734f9cc0e77d01`) |
| 06 | Hierarchy and transforms | PASS | Job `d7ce733cd3c648d0880ed007841e5d29` completed; all 17 asset objects parented to Kart01_Root with applied transforms; blend at `artifacts/blend/Kart01.blend` (sha256 `59f462e89827b97590a27f93ce53116361d4c70c8a975488acd9896f3b6c6f60`) |
| 07 | Presentation cameras and lighting | PASS | Rendered 4 PNG images (perspective, front, side, rear) at 512x512 resolution; saved to artifacts/renders/ |
| 08 | Final validation | NOT_STARTED | |
| 09 | Export and delivery | NOT_STARTED | |

## Start instruction

Read `HANDOFF.md` and `WORKER_GUIDE.md`, run `python3 scripts/check_resume.py`, check current worker capabilities, and record the actual selected model. This reset is verified fresh, so begin Stage 00 with a new empty isolated scene and no historical `source_job`. Keep this file and HANDOFF.md current after each accepted ID before polling and after every result. Later sessions must reconcile/resume their recorded source and pending job rather than assume the run is fresh.

## Historical evidence

- The latest 65K build is preserved in `artifacts/archive/blender35b-65k-build-2026-10-22/`. Its ledger claimed Stage 00 PASS but still said NOT_STARTED/no active source; that inconsistency and all local work are preserved for review. No stage PASS is reused.
- The failed Blender-specialist attempt is preserved in `artifacts/archive/blender35b-attempt-2026-10-22/`, including Stage 00 source, exact remote submissions, diagnostics, and setup snapshots. No stage PASS is reused.
- The latest Qwen27B attempt is preserved in `artifacts/archive/qwen27b-attempt-2026-10-22/`, including its original ledger, 19 downloaded job-metadata directories, and setup snapshots. See `ATTEMPT_NOTES.md`. Its claimed stage results are not reused.
- The interrupted Defiant Fable attempt is preserved in `artifacts/archive/defiant-fable-2026-10-22/`. See `ATTEMPT_REVIEW.md` for the execution-guard diagnosis and historical job IDs. No stage was independently verified as PASS.
- The reviewed run, original rules/configuration, scripts, downloads, outputs, and independent review are preserved in `artifacts/archive/pre-reset-2026-10-22/`.
- The earlier run remains in `artifacts/archive/pre-z6-2026-10-21/`.
- Historical job IDs and stage results belong only to those runs.

## Reset verification (setup evidence, not a build PASS)

- All 10 stages are NOT_STARTED; active blend/export/render/download/report directories contain no generated outputs.
- `artifacts/scripts/` retains only its placeholder and the unchanged model-discovery utility.
- `spec/kart-01/` is unchanged. The Blender-specialist model is now configured and runtime-verified at 102,400 tokens. HANDOFF.md and the read-only resume preflight guard against stale ledger restarts.
- Historical archives are retained. The latest archive includes a SHA-256 file manifest; archived metadata is not current build evidence.
- Worker diagnostics runtime `6cd1b81` is installed on Z6; installed CPU/CUDA fixtures and the separately labelled guided model recovery check passed. The strict unguided model recovery check failed and remains documented in the worker's diagnostics report. Those fixture jobs are not Kart01 build stages.
- Start a new OpenCode session to avoid inherited conversation context. No build job has been submitted for this run.
