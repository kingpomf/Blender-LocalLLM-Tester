# Operator-authorized controlled continuation

**Prepared; not started.** The user will invoke this continuation.

From the project directory:

```sh
python3 scripts/run_bowling.py --check-continuation
python3 scripts/run_bowling.py --resume --continuation --detach
```

Or fully restart OpenCode and invoke `/bowling-continue` once. Do not use the
fresh-run launcher or clear `.runtime` for this continuation.

## Authority and fixed identities

- Agent: `z6-llama/qwen36-35b-a3b-mtp-q8`, existing retuned native256K profile.
- Same trial: `bowling52-qwen36-mtp-q8-20261023-r2`.
- Same durable failure history:6 failed jobs retained; limits increased to6/source
  and12/trial, as explicitly requested. No budget reset or new trial.
- Starting source: **`d1ce998472c349ac9f9fc2775afefdf6`**.
- Canonical scene: `artifacts/blend/BowlingPair01.blend`, verified hash
  `4480223492c6790eceb0e66729cd5e99b15ee8875c25c45cfeab76af521bd017`.
- Reference phase is already READY; do not regenerate its three images.

## Required first actions

1. Read both ledgers and `testing/BALL_GENERATION_DIAGNOSTICS.md`.
2. Run the exact commands without shell redirects or chained shell operations:
   `python3 scripts/check_resume.py` and `python3 scripts/check_references.py`.
3. Confirm MCP capabilities show6/source,12/total and the same r2 queue.
4. Inspect the existing source. It is integrity-verified and completed, but has
   measured Stage01–03 defects. Repair the floating markings, malformed gutters,
   reversed pin rows, missing bands and open pin seam before accepting those stages.
5. Diagnose and repair Stage04 using actual supported APIs. The saved
   `extrude_region_unshared` call is invalid. Follow the diagnostic report's
   geometry/separation/measurement findings, not the prior agent's inaccurate summary.
6. Save each corrected script, inspect Pyright/API diagnostics and submit a real
   changed revision from the last completed source. Record accepted IDs before
   polling and never treat failed jobs as sources. Use valid run/stage statuses.
   After verified artifact download, copy the checkpoint using separate allowed
   commands with project-relative paths (replace COMPLETED_ID with the actual ID):
   `cp artifacts/downloads/COMPLETED_ID/scene.blend artifacts/blend/BowlingPair01.blend`,
   then `shasum -a 256 artifacts/blend/BowlingPair01.blend`. The directory already
   exists; do not chain mkdir/cp/hash commands or substitute Linux sha256sum on Mac.
7. Continue stages through09 with compaction/checkpoints, stopping for true
   blockers or exhausted limits. This is a labeled continuation with operator
   diagnostic assistance, not an unaided fresh model result.

The read-only operator audit did not repair any asset or clear failure history.
An authorization manifest binds this handoff to the reconciled source, canonical
hash and guard rows. The explicit continuation preflight refuses changed or pending
work instead of silently starting with a different scene.
