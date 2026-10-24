# BowlingPair01 Session Handoff — fresh Nemotron trial

IN_PROGRESS
- Current stage: 00 — Contract and scene safety
- Last verified source job: none
- Pending job: none
- Pending source job: none
- Latest verified local checkpoint: artifacts/blend/BowlingPair01.blend
- Next action: Proceed to Stage 01. Review specifications in spec/bowling-pair-01/ and prepare code for next stage.
- Trial queue: var/bowling52-nemotron-20261023
- Trial mode: 65,536-token context; automatic compaction/pruning OFF; 60 iterations per turn

This reset was explicitly authorized on 2026-10-23. The old checkpoint, all
model-authored scripts and exhausted guard were archived at
`artifacts/archive/blender52-specialist-final-2026-10-23/`. No historical source,
implementation or stage PASS is reused. The new tool-owned guard starts empty.

Keep source IDs bare. Immediately record accepted IDs and pending source in both
ledgers before polling; retain the last verified completed source until measured
acceptance passes. Stage result and overall run status are distinct: overall
status must be NOT_STARTED, IN_PROGRESS, FAIL, BLOCKED or COMPLETE. Update all
related metadata together, then run `python3 scripts/check_resume.py`.

On a tool STOP, save evidence and return BLOCKED. Do not clear/bypass guard state.
