---
description: Verify the 5.2 toolchain and build or resume ONE bowling stage
agent: build
---

Build or resume exactly one stage of BowlingPair01, then checkpoint and return
to the user. Read AGENTS.md, BUILD_STATUS.md, HANDOFF.md, RUNTIME_52.md,
WORKER_GUIDE.md and the relevant specifications. Before initial Stage 00, read
all ten files in spec/bowling-pair-01/ to plan the assembly.

FIRST call capabilities through the distinct `bowling-blender52` connection.
Require runtime_verified=true, actual_version="Blender 5.2.3 LTS", and root ending
`var/bowling52-nemotron-20261023`. If this connection is missing, STOP and ask for a
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

On any tool STOP, duplicate-rejection or exhausted budget, save evidence and
return BLOCKED immediately. No repeated blocked calls, guard resets or bypasses.
The Build-agent turn has a 60-step limit. Complete the current stage or checkpoint
partial work, then return for the operator to invoke the next stage. Preserve the
64K/no-compaction settings. Use CPU renders only. Do not edit test infrastructure,
commit or push. All archived attempts are evidence, not starting assets.
