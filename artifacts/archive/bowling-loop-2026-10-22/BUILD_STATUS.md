# BowlingPair01 Build Status

- Status: IN_PROGRESS
- Next stage: 03 — Reusable bowling pins
- Active source job: 60dc79d835ea42e6914b82d4382870b0 (Stage 03 in progress)
- Accepted job IDs: d5c68e4d5c834c378c60a77882ab00be (original Stage 00); 8392bbe3487c49e4b068da8424cb5fdd, 83522d1932994c44ba0955941768d924, 7317961b8dd042ba8f7fca1132687618, 38d4ec505d2248c29d368d14c3bda4a6, e547b3da598f4ed0b8f920ed4e4509f9, 6237cb6f2e3b430a9cb788686cba08a3 (failed historical 4.5 Stage 01 attempts); c0015706160d4e8c959508dd011e2074 (repaired Stage 00)
- Default model: `z6-llama/qwen38-blender-35b` — 262,144-token context
- Actual model used: `z6-llama/qwen38-blender-35b` in session ses_e9b614548ffeNVD6ktiZPPiyIR
- Execution host: Z6 (`z6-blender-worker`), project-only `var/bowling-blender52` queue
- Runtime: Blender 5.2.3 LTS; rendering CPU-only for this test
- Operator intervention: 5.2.3 installed alongside 4.5.14, project stubs changed to fake-bpy-module-5.2 20260730, failed foundation reclassified after native reopen inspection
- Trial mode: automatic compaction and pruning OFF; no manual compaction; runtime intervention makes continuation a separately labelled evaluation
- Active checkpoint: artifacts/blend/BowlingPair01.blend (Stage 02 PASS, SHA-256 af5a71084b9b9c1a002b133003918c77b268781de33d372fb69bc0ca479f3aa1)

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PASS | Collections BP01_STATIC, BP01_PINS, BP01_BALLS, BP01_COLLISION, BP01_PRESENTATION linked into scene.collection; empty root BowlingPair01_ROOT at origin with identity transform; metric units with scale 1.0 verified |
| 01 | Lane pair and markings | PASS | Lane surfaces (1.0668m wide, Y=0..19.20), approaches (Y=-4.572..0), foul line strips, 14 arrows (7 per lane), 14 dots (7 per lane) created and linked to BP01_STATIC |
| 02 | Gutters, decks and pit | PASS | Four gutters (outer/inner per lane), pin decks, central divider, and rear pit regions created and linked to BP01_STATIC |
| 03 | Reusable bowling pins | NOT_STARTED | |
| 04 | Reusable bowling balls | NOT_STARTED | |
| 05 | Return, seating and alley dressing | NOT_STARTED | |
| 06 | Materials, hierarchy and collision | NOT_STARTED | |
| 07 | Presentation cameras and lighting | NOT_STARTED | |
| 08 | Final measured validation | NOT_STARTED | |
| 09 | Export and delivery | NOT_STARTED | |

## Next action

Submit Stage 01 (Lane pair and markings) using source job c0015706160d4e8c959508dd011e2074. Create two lane surfaces (1.0668m wide, Y=0..19.20), two approaches (Y=-4.572..0), foul line strip, seven arrows per lane, seven dots per lane, and pin-deck overlay pieces. Measure world-space bounds, spacing, surface height and marking counts.

The original checkpoints are in `testing/blender52/before-*.md`. Original failed
jobs remain in `var/mcp-worker` and are not pending in the new queue. Runtime
qualification jobs in `testing/blender52/runtime-evidence.json` are infrastructure
evidence, not bowling stage passes. The old kart archive remains preserved under
`artifacts/archive/kart256k-before-bowling-2026-10-22/`.
