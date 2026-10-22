# Kart01 Build Status

## Fresh test — reset after Blender-specialist attempt and diagnostics repair, 2026-10-22

- Status: NOT_STARTED
- Next stage: 00 — Contract and scene safety
- Active source job: none
- Accepted job IDs: none for this run
- Default model: `z6-llama/qwen38-blender-35b` — Qwen3.8 35B A3B Blender v1, 65,536-token context; the operator may select another configured model before `/kart-start`.
- Actual model used: not yet recorded
- Execution host: Z6 (`z6-blender-worker`)
- Operator intervention: none in this run
- Active outputs: cleared; no previous PASS is reused

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | NOT_STARTED | |
| 01 | Coordinate system and dimensions | NOT_STARTED | |
| 02 | Chassis and bumpers | NOT_STARTED | |
| 03 | Axles and wheels | NOT_STARTED | |
| 04 | Seat and steering | NOT_STARTED | |
| 05 | Materials | NOT_STARTED | |
| 06 | Hierarchy and transforms | NOT_STARTED | |
| 07 | Presentation cameras and lighting | NOT_STARTED | |
| 08 | Final validation | NOT_STARTED | |
| 09 | Export and delivery | NOT_STARTED | |

## Start instruction

Read `WORKER_GUIDE.md`, check current worker capabilities, record the actual selected model, and begin Stage 00 with a new empty isolated scene. Do not supply a historical `source_job`. Call stage functions unconditionally, then chain later stages using the preceding verified authoring job ID. Fetch/read `scene.json` and `report.json` before declaring stage PASS. Record each accepted job ID before polling and save verified outputs at the required paths.

## Historical evidence

- The failed Blender-specialist attempt is preserved in `artifacts/archive/blender35b-attempt-2026-10-22/`, including Stage 00 source, exact remote submissions, diagnostics, and setup snapshots. No stage PASS is reused.
- The latest Qwen27B attempt is preserved in `artifacts/archive/qwen27b-attempt-2026-10-22/`, including its original ledger, 19 downloaded job-metadata directories, and setup snapshots. See `ATTEMPT_NOTES.md`. Its claimed stage results are not reused.
- The interrupted Defiant Fable attempt is preserved in `artifacts/archive/defiant-fable-2026-10-22/`. See `ATTEMPT_REVIEW.md` for the execution-guard diagnosis and historical job IDs. No stage was independently verified as PASS.
- The reviewed run, original rules/configuration, scripts, downloads, outputs, and independent review are preserved in `artifacts/archive/pre-reset-2026-10-22/`.
- The earlier run remains in `artifacts/archive/pre-z6-2026-10-21/`.
- Historical job IDs and stage results belong only to those runs.

## Reset verification (setup evidence, not a build PASS)

- All 10 stages are NOT_STARTED; active blend/export/render/download/report directories contain no generated outputs.
- `artifacts/scripts/` retains only its placeholder and the unchanged model-discovery utility.
- `spec/kart-01/` is unchanged. Agent/worker/kickoff guidance now describes zero-object startup, exact scene/unit API, and bounded failed-job diagnostics. The 65,536-token Blender-specialist model remains selected.
- Historical archives are retained. The latest archive includes a SHA-256 file manifest; archived metadata is not current build evidence.
- Worker diagnostics runtime `6cd1b81` is installed on Z6; installed CPU/CUDA fixtures and the separately labelled guided model recovery check passed. The strict unguided model recovery check failed and remains documented in the worker's diagnostics report. Those fixture jobs are not Kart01 build stages.
- Start a new OpenCode session to avoid inherited conversation context. No build job has been submitted for this run.
