---
description: Build or resume all remaining bowling stages continuously through delivery
agent: build
model: z6-llama/qwen36-35b-a3b-mtp-q8
---

Build or resume all remaining stages of BowlingPair01 through verified delivery.
Do not stop after a stage or ask the user to say next. Read AGENTS.md,
BUILD_STATUS.md, HANDOFF.md, RUNTIME_52.md,
WORKER_GUIDE.md and the relevant specifications. Before initial Stage 00, read
all ten files in spec/bowling-pair-01/ to plan the assembly.

BEFORE Blender authoring, read REFERENCE_IMAGES.md and run the reference checker.
If the reference phase is not READY, return and ask the operator to invoke
`/bowling-references`, which also uses Qwen3.6 and its fixed image-description
helper. Do not claim this text-only MTP profile can view pixels itself.
After that phase passes, this command begins Stage 00 using its saved visual guide.

FIRST call capabilities through the distinct `bowling-blender52` connection.
Require runtime_verified=true, actual_version="Blender 5.2.3 LTS", and root ending
`var/bowling52-qwen36-mtp-q8-20261023-r2`. If this connection is missing, STOP and ask for a
full OpenCode restart. Do not use z6-blender-worker or other Blender tools.
Run `python3 scripts/check_resume.py`. Reconcile pending work before submission.

Record the actual selected model. Only a fresh NOT_STARTED run begins without a
source_job. Later work uses the last verified completed 5.2 source. Save each
script and check its LSP/Pyright diagnostics before submission; call functions
unconditionally and assign a meaningful top-level report. Runtime assertions in
the wrapper do not prove stage acceptance. Measure actual geometry and reopen
saved native scenes to verify persistence.

Record each accepted job, source and pending state in BOTH checkpoints before
polling. Keep Active source / Last verified source as the previous verified bare
job ID until the new scene passes. Save a hash-verified native checkpoint after
acceptance. Never mark a stage PASS based on constants or script existence.

For native publication use `python3 scripts/checkpoint_bowling.py --source COMPLETED_ID`.
For measured acceptance use `python3 scripts/validate_checkpoint.py --campaign UNIQUE_ID`,
then `python3 scripts/checkpoint_bowling.py --sync-ledgers`. These update both
ledgers deterministically; do not guess stale oldString text or duplicate stage rows.
Read all FAIL/unresolved findings and repair actual geometry/evidence. The fixed
operator-reviewed validator must not be weakened or replaced with existence checks.

On any tool STOP, duplicate-rejection or exhausted budget, save evidence and
return BLOCKED immediately. No repeated blocked calls, guard resets or bypasses.
After each stage passes, update both ledgers, save the verified native checkpoint,
run the consistency check, then immediately continue to the next stage. Automatic
compaction/pruning are enabled and the60-step cap is removed. Before compaction,
checkpoint pending IDs, verified source, measurements and next action; afterward
reread the ledgers/reference guide and resume without replaying accepted work.
Return only at COMPLETE or a genuine BLOCKED/FAIL/user-stop condition.
Use CPU renders only. Do not edit test infrastructure,
commit or push. All archived attempts are evidence, not starting assets.

Controller recovery context, when present:
$ARGUMENTS
