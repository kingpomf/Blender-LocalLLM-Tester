---
description: Build or resume the staged BowlingPair01 alley asset challenge
---

Build the active BowlingPair01 assignment. Read RUNTIME_52.md, AGENTS.md, BUILD_STATUS.md,
HANDOFF.md, WORKER_GUIDE.md, LSP_SETUP.md and all ten files in
spec/bowling-pair-01/. Run `python3 scripts/check_resume.py` before submitting.
Reconcile any inconsistent progress; poll a recorded pending job rather than
starting over. Historical kart artifacts are not sources for this build.

Verify the project-only Blender 5.2.3 Z6 queue, authoring availability and job diagnostics. Use CPU renders only. The preserved foundation currently needs Stage 00 repair; do not reuse its historical PASS or start over. Record the
actual selected model. Work through Stages 00–09 in order. Only a fresh run starts
with no source_job and zero objects; every later stage uses the last verified
same-host source. Save each script and inspect LSP/Pyright diagnostics before
submission. Execute stage functions unconditionally at top level.

Record accepted job ID, stage, source and pending state in BOTH checkpoints
before polling. Fetch/read scene.json and meaningful report.json, measure actual
geometry, and save a hash-verified BowlingPair01.blend after each passed stage.
Execution success alone is not acceptance. Use bounded traceback-specific repairs
and revalidate affected requirements. Keep the 256K trial in one session with no
manual compaction; checkpoint and report context exhaustion if needed.

Create the two-lane alley, reusable props and collision proxies, then render all
four specified views using real cameras. Export and round-trip the pair, pin,
three balls and collision GLBs; verify portable materials, units, pivots, counts
and hashes. Keep game-integration notes and objective validation evidence. Mark
COMPLETE only after every required check passes. Preserve archives and protected
workloads. Do not commit or push without approval.
