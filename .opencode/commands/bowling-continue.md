---
description: Explicitly resume the current Qwen3.8 Turbo trial after reconciliation
agent: build
model: z6-llama/qwen38-turbo
---

Inspect `python3 scripts/run_bowling.py --status`. Do not start a duplicate.
Resume only when the operator explicitly requested it and the recorded blocker
and accepted pending jobs have been reconciled. Preserve current trial history.
Use `python3 scripts/run_bowling.py --resume --detach` for an authorized ordinary
interruption. A checkpoint-bound operator continuation additionally requires
`--check-continuation` and `--continuation`; do not use retired trial plans.
Never clear budgets, switch sources to evade limits or replay uncertain requests.
Report actual process/session state; starting is not asset acceptance.
