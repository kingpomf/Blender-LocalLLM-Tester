# BowlingPair01 Session Handoff — fresh Qwen3.6 MTP Q8 trial

- Run status: NOT_STARTED
- Current stage: 00 — Contract and scene safety
- Last verified source job: none
- Pending job: none
- Pending source job: none
- Latest verified local checkpoint: none
- Next action: Fully restart OpenCode; new Qwen3.6 MoE session; run /bowling-run once. Every agent phase is pinned to Qwen3.6; inspect scripts/run_bowling.py --status for progress.
- Reference phase: NOT_STARTED
- Pending reference job: none
- Trial queue: var/bowling52-qwen36-mtp-q8-20261023-r2
- Trial mode: native262,144-token context; automatic compaction/pruning ON;16,384-token reserve; continuous stages with no configured step cap

The operator authorized this reset on 2026-10-23 after ending the previous test.
The later wrong-model startup was also explicitly reset. Its blocked controller,
session events and empty guard are preserved at
`artifacts/archive/qwen38-startup-failed-20261023/`. No image/Blender jobs were
submitted; the new r2 queue and controller state start fresh.
All old output, original ledgers and guard state are hash-archived at
`artifacts/archive/nemotron-final-before-qwen36-2026-10-23/`. All accepted jobs
were confirmed terminal remotely; none was replayed. The new guard is empty.
No old implementation, source ID or PASS is reused.

Record accepted IDs and pending source in both ledgers before polling. Keep
the last verified completed source until actual acceptance passes. Update both
ledgers after every terminal result, then run `python3 scripts/check_resume.py`.
On any tool STOP, checkpoint and return BLOCKED. Do not reset or bypass the guard.
