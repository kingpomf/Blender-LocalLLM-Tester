---
description: Build or resume the simplified three-phase kart
---
Read AGENTS.md, spec/KART_SIMPLIFIED.md, WORKER_GUIDE.md, and RUN_STATE.json. Run python3 scripts/check_resume.py. Reconcile pending jobs and existing outputs before authoring. Use BUILD → REVIEW → DELIVER, recording accepted IDs before polling in RUN_STATE.json only. Use supplied helpers, fixed presentation, and unchanged validator. Never reuse historical stage passes. Preserve active/protected workloads and archives. Do not commit or push without authorization.
