# Kart01 Build Status

## Fresh test — 2026-10-22

- Status: NOT_STARTED
- Next stage: 00 — Contract and scene safety
- Active source job: none
- Accepted job IDs: none for this run
- Default model: `z6-llama/qwen38-27b`; the operator may select another configured model before `/kart-start`.
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

Check the current worker capabilities, record the actual selected model, and begin Stage 00 with a new empty isolated scene. Do not supply a historical `source_job`. Record each accepted job ID before polling and save verified outputs at the required paths.

## Historical evidence

- The reviewed run, original rules/configuration, scripts, downloads, outputs, and independent review are preserved in `artifacts/archive/pre-reset-2026-10-22/`.
- The earlier run remains in `artifacts/archive/pre-z6-2026-10-21/`.
- Historical job IDs and stage results belong only to those runs.

## Reset verification (setup evidence, not a build PASS)

- Installed OpenCode `1.18.34` successfully loaded the revised configuration with `opencode debug config`.
- `opencode mcp list` confirmed `z6-blender-worker` connected; the other six configured MCP servers remain disabled.
- All 10 stages are NOT_STARTED; active blend/export/render/download/report directories contain no generated outputs.
- `spec/kart-01/` is unchanged from Git HEAD; `git diff --check` passed.
- The archive contains 66 SHA-256-indexed files in `ARCHIVE_MANIFEST.json`; original scene, GLB, and inspection-metadata hashes were independently verified.
- Start a new OpenCode session after restarting to avoid inherited conversation context. No build job has been submitted for this run.
