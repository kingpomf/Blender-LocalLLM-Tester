# Kart01 Build Status

## Run metadata

- Status: READY — repairs verified on Z6; no Kart01 build submitted
- Active stage: 00
- Model: `z6-llama/qwen38-27b` (Qwen3.8 27B Dense)
- Execution host: Z6 (`z6-blender-worker`)
- Previous run: preserved under `artifacts/archive/pre-z6-2026-10-21/`
- Blender version: NOT RECORDED
- Worker status: authoring.available=true; installed runtime hashes verified; gateway healthy, CODING_PROTECTED / ready
- Started (UTC): NOT STARTED
- Last updated (UTC): 2026-10-21

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PENDING | Authoring and review repairs installed and verified; ready for a fresh Kart01 scene. |
| 01 | Coordinate system and dimensions | PENDING | — |
| 02 | Chassis and bumpers | PENDING | — |
| 03 | Axles and wheels | PENDING | — |
| 04 | Seat and steering | PENDING | — |
| 05 | Materials | PENDING | — |
| 06 | Hierarchy and transforms | PENDING | — |
| 07 | Presentation cameras and lighting | PENDING | — |
| 08 | Final validation | PENDING | — |
| 09 | Export and delivery | PENDING | — |

## Current blocker

None. Review findings R1–R3 were repaired and installed from worker commit `82a62e0`. Original-topology reporting, disconnected STL rejection, packed texture round-trip/CPU/CUDA rendering, explicit dependency errors, and deployment cleanup/rollback checks passed. The review hold is lifted. These fixture checks are not Kart01 stage passes. See `artifacts/reports/Z6_RESET.md` for evidence.

Resolved: the initial `RECOVERY_REQUIRED` state was cleared on 2026-10-21 with the user's explicit authorization using `POST /recovery/reconcile`. The later authoring deployment used a guarded gateway restart with model-service identities preserved. After a real CUDA fixture render, gateway health is `ok`, state `CODING_PROTECTED`, handoff `ready`. Both initial blockers are resolved.

See `artifacts/reports/Z6_RESET.md` for setup and verification evidence.

## Resume instruction

Restart OpenCode and run `/kart-start`. Verify `authoring.available=true`, inspect a new empty isolated scene, then begin Stage 00 via `blender_scene_author`. Record accepted job/source IDs before polling, fetch the verified artifacts, and copy/hash-check the required local checkpoint. The previous run's PASS remains archived.
