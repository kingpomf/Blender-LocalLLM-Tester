# BowlingPair01 Session Handoff

**Model replacement — 2026-10-23:** selected `z6-llama/nemotron35-bolt-e4b` with
65,536-token context. The old model was retired; the run below is historical
Blender-specialist work, not Nemotron work. Its guard budget is exhausted and
remains intact. Do not submit a new model against it without operator-directed
trial preparation. No new asset stage was built during model installation.

- Run status: IN_PROGRESS
- Current stage: 04 — Reusable bowling balls
- Last verified source job: 196cdb8cfa614597a323a7669b7a28bc
- Pending job: none
- Pending source job: none
- Latest verified local checkpoint: artifacts/blend/BowlingPair01.blend (sha256: 61a1a6d8cb96c2b789147df51248692251f40d2b110cacd7cf2299b49348665b)
- Next action: Submit Stage 04 ball geometry from source job 196cdb8cfa614597a323a7669b7a28bc.
- Trial mode: guarded 5.2 trial; 60 Build-agent steps per turn; automatic compaction/pruning OFF

Keep source IDs bare, without parenthetical text. The verified source stays
unchanged when submitting a job; put its new ID in Pending job and record its
source separately. Update both checkpoints before polling and after each result.
Execution success is not measured stage acceptance. A failed/pending job is never
the verified source. Tool-owned `.runtime/blender52/submissions.sqlite` also
records accepted IDs, uncertain submissions and durable failure budgets.

On any STOP/circuit-breaker error, save evidence and return BLOCKED. Do not clear
guard state, change tools, switch queues or repeatedly call a blocked submission.
Original work is preserved in `artifacts/archive/bowling-loop-2026-10-22/`.
