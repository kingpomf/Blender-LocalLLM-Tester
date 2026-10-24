---
description: Start the explicitly authorized reconciled Qwen3.6 continuation with doubled failure limits
agent: build
model: z6-llama/qwen36-35b-a3b-mtp-q8
---

The operator authorized reconciliation, diagnostic assistance and6/source12/total
failure limits while retaining all prior failures. They are now explicitly
invoking this continuation command.

First run `python3 scripts/run_bowling.py --check-continuation`. If it passes, run
`python3 scripts/run_bowling.py --resume --continuation --detach` once. Do not
also author a scene from this launcher session or start a second controller.
The controller will use the existing Qwen3.6 coding session, saved reference
guide and verified source, with the explicit diagnostic handoff supplied.

If preflight fails or another controller holds the lock, report the exact issue
without overriding it. Return the controller PID and status/log paths; starting
the continuation is not proof of asset completion.
