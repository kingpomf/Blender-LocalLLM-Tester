# BowlingPair01 Session Handoff

- Run status: NOT_STARTED
- Current stage: 00 — Contract and scene safety
- Last verified source job: none
- Pending job: none
- Pending source job: none
- Latest verified local checkpoint: none
- Next action: New OpenCode process/session; `/bowling-start`; require bowling-blender52 capabilities and actual Blender 5.2.3 LTS, then build and verify Stage 00 only.
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
