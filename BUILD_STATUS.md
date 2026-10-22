# BowlingPair01 Build Status

- Status: NOT_STARTED
- Next stage: 00 — Contract and scene safety
- Active source job: none
- Accepted job IDs: none
- Default model: `z6-llama/qwen38-blender-35b` — 262,144-token context
- Actual model used: not yet recorded
- Execution host: Z6 (`z6-blender-worker`)
- Operator intervention: new bowling assignment prepared; no bowling jobs submitted
- Trial mode: automatic compaction and pruning OFF; no manual compaction
- Active checkpoint: artifacts/blend/BowlingPair01.blend (not yet created)

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | NOT_STARTED | |
| 01 | Lane pair and markings | NOT_STARTED | |
| 02 | Gutters, decks and pit | NOT_STARTED | |
| 03 | Reusable bowling pins | NOT_STARTED | |
| 04 | Reusable bowling balls | NOT_STARTED | |
| 05 | Return, seating and alley dressing | NOT_STARTED | |
| 06 | Materials, hierarchy and collision | NOT_STARTED | |
| 07 | Presentation cameras and lighting | NOT_STARTED | |
| 08 | Final measured validation | NOT_STARTED | |
| 09 | Export and delivery | NOT_STARTED | |

## Next action

Read AGENTS.md, HANDOFF.md, WORKER_GUIDE.md and all ten bowling specifications.
Run `python3 scripts/check_resume.py`, verify capabilities and record the actual
selected model. Start Stage 00 with no source_job only while this run is fresh.
Record every accepted ID and its source here and in HANDOFF.md before polling.
After verification, save the hash-verified native checkpoint and update both
documents before advancing. A failed required check remains FAIL.

## Previous project

Kart work and its original claims are preserved verbatim under
`artifacts/archive/kart256k-before-bowling-2026-10-22/`, with a SHA-256 manifest.
Those claims were not independently certified during setup. Large native scenes
and job metadata remain local ignored archive files; the snapshot commit also
preserves the prior tracked setup. Older archives and `spec/kart-01/` remain
historical. No historical job, source, script or PASS belongs to this bowling run.
