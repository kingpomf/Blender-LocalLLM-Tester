---
description: Build or resume the simplified three-phase kart
agent: build
model: z6-llama/qwen38-flash-next
---
Read AGENTS.md, spec/KART_SIMPLIFIED.md, WORKER_GUIDE.md, and RUN_STATE.json. Run python3 scripts/check_resume.py. Reconcile pending jobs and existing outputs before authoring. Use BUILD → REVIEW → DELIVER, recording accepted IDs before polling in RUN_STATE.json only. Use supplied helpers, fixed presentation, and unchanged validator. Never reuse historical stage passes. Preserve active/protected workloads and archives. Do not commit or push without authorization.

Current trial uses Qwen3.8 Flash-Next through Strata, not the retired Turbo or
Blender-specialist profile. Start from this clean trial's RUN_STATE only. Record
status RUNNING (not IN_PROGRESS), actual model, accepted IDs and real timestamps.
Use `date -u +%Y-%m-%dT%H:%M:%SZ` for a timestamp, or omit optional timestamps
when unavailable; never invent a midnight time.
Bounded sleeps1/2/5/10/15 are permitted for polling; a wait is not a build result.
Poll each accepted job to terminal. If it fails, read diagnostics once, record
failed/null pending state and make a genuine correction. Do not stop merely after
submission or treat exit0 as asset acceptance. No identical failed resubmission.
Use relative paths for allowed checkpoint copies, for example:
cp artifacts/downloads/JOB/scene.blend artifacts/blend/Kart01.blend
Keep Read output bounded. Do not edit supplied support/spec/checker code.
