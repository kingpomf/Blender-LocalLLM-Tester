# BowlingPair01 Build Status

- Status: IN_PROGRESS
- Next stage: 01 — Lane pair and markings
- Active source job: d5c68e4d5c834c378c60a77882ab00be
- Accepted job IDs: d5c68e4d5c834c378c60a77882ab00be (Stage 00), 8392bbe3487c49e4b068da8424cb5fdd (Stage 01 failed), 83522d1932994c44ba0955941768d924 (Stage 01 retry)
- Default model: `z6-llama/qwen38-blender-35b` — 262,144-token context
- Actual model used: `z6-llama/qwen38-blender-35b`
- Execution host: Z6 (`z6-blender-worker`)
- Operator intervention: new bowling assignment prepared; no bowling jobs submitted
- Trial mode: automatic compaction and pruning OFF; no manual compaction
- Active checkpoint: artifacts/blend/BowlingPair01.blend (not yet created)

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PASS | Collections, units, root at origin verified; checkpoint saved |
| 01 | Lane pair and markings | IN_PROGRESS | Source job 8392bbe3487c49e4b068da8424cb5fdd accepted |
| 02 | Gutters, decks and pit | NOT_STARTED | |
| 03 | Reusable bowling pins | NOT_STARTED | |
| 04 | Reusable bowling balls | NOT_STARTED | |
| 05 | Return, seating and alley dressing | NOT_STARTED | |
| 06 | Materials, hierarchy and collision | NOT_STARTED | |
| 07 | Presentation cameras and lighting | NOT_STARTED | |
| 08 | Final measured validation | NOT_STARTED | |
| 09 | Export and delivery | NOT_STARTED | |

## Next action

Submit Stage 01 (Lane pair and markings) using source job d5c68e4d5c834c378c60a77882ab00be. Create two lane surfaces (1.0668m wide, Y=0..19.20), two approaches (Y=-4.572..0), foul line strip, seven arrows per lane, seven dots per lane, and pin-deck overlay pieces. Measure world-space bounds, spacing, surface height and marking counts.

## Previous project

Kart work and its original claims are preserved verbatim under
`artifacts/archive/kart256k-before-bowling-2026-10-22/`, with a SHA-256 manifest.
Those claims were not independently certified during setup. Large native scenes
and job metadata remain local ignored archive files; the snapshot commit also
preserves the prior tracked setup. Older archives and `spec/kart-01/` remain
historical. No historical job, source, script or PASS belongs to this bowling run.
