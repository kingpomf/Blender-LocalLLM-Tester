---
description: Report why the bowling trial is paused
agent: build
---

Do not execute the historical continuation instructions below. Tell the user
that the original Z6 model was retired and the trial requires explicit migration.

Inspect `python3 scripts/run_bowling.py --status`. Do not start a duplicate.
Resume only when the operator explicitly requested it and the recorded blocker
and accepted pending jobs have been reconciled. Preserve current trial history.
Use `python3 scripts/run_bowling.py --resume --detach` for an authorized ordinary
interruption. A checkpoint-bound operator continuation additionally requires
`--check-continuation` and `--continuation`; do not use retired trial plans.
Never clear budgets, switch sources to evade limits or replay uncertain requests.
Report actual process/session state; starting is not asset acceptance.
