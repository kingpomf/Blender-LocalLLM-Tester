# Kart01 Build Status

## Fresh test — reset after interrupted Defiant Fable attempt, 2026-10-22

- Status: IN_PROGRESS
- Next stage: 02 — Chassis and bumpers
- Active source job: 742a1f200bac450382529e18594f4e99
- Accepted job IDs: 7399670c3256418f99c46714161d6a0f (Stage 00)
- Default model: `z6-llama/qwen38-27b`; the operator may select another configured model before `/kart-start`.
- Actual model used: z6-llama/qwen38-27b
- Execution host: Z6 (`z6-blender-worker`)
- Operator intervention: none in this run
- Active outputs: cleared; no previous PASS is reused

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PASS | Job 7399670c3256418f99c46714161d6a0f: collections KART01_ASSET, KART01_PRESENTATION, METRIC units, scale 1.0 |
| 01 | Coordinate system and dimensions | PASS | Job 742a1f200bac450382529e18594f4e99: 12 reference objects (REF_X/Y/Z_MAX, REF_GROUND, REF_WB*/FT*/RT*, REF_WHEEL) at spec positions |
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

- The interrupted Defiant Fable attempt is preserved in `artifacts/archive/defiant-fable-2026-10-22/`. See `ATTEMPT_REVIEW.md` for the execution-guard diagnosis and historical job IDs. No stage was independently verified as PASS.
- The reviewed run, original rules/configuration, scripts, downloads, outputs, and independent review are preserved in `artifacts/archive/pre-reset-2026-10-22/`.
- The earlier run remains in `artifacts/archive/pre-z6-2026-10-21/`.
- Historical job IDs and stage results belong only to those runs.

## Reset verification (setup evidence, not a build PASS)

- Installed OpenCode `1.18.34` successfully loaded the revised configuration with `opencode debug config`.
- `opencode mcp list` confirmed `z6-blender-worker` connected; the other six configured MCP servers remain disabled.
- All 10 stages are NOT_STARTED; active blend/export/render/download/report directories contain no generated outputs.
- `spec/kart-01/` is unchanged from Git HEAD; `git diff --check` passed.
- The previous reset archive retains its original 66-file manifest. The Defiant Fable archive contains 33 SHA-256-indexed files in its own `ARCHIVE_MANIFEST.json`; the diagnosed empty scene's hash was verified. Archived files are not current build evidence.
- Both known AI-video jobs from the interrupted attempt were checked and were already completed. No new remote build/render/generation jobs were submitted during reset.
- Start a new OpenCode session after restarting to avoid inherited conversation context. No build job has been submitted for this run.
