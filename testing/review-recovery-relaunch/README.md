# Automatic review reconciliation and authorized relaunch

The user authorized resolving the stuck image-review workflow, detached relaunch,
and automatic handling of this failure mode. No failure-budget reset was requested.

## Fix and acceptance boundaries

Every MCP workflow call now reconciles nonterminal reviews before status/admission.
Saved completed results are consumed once; ended/expired helpers and malformed
results become terminal failures. The same request is never automatically replayed.
Helper responses/results are saved atomically so malformed responses leave evidence.

All view roles, source/image lineage, Boolean verdicts and detailed observations
are checked before evidence publication. Short optional criterion notes are omitted
with explicit warnings, leaving the original criterion unresolved. No text padding,
inferred visibility, relaxed validator threshold or automatic PASS is introduced.
Repeated status calls return cached terminal results without republishing evidence.

## Verification

- **91 unit tests passed**, targeted Pyright **0 errors/warnings**.
- Regression tests cover saved-result recovery with short notes, insufficient
  positive evidence, malformed results releasing admission without partial
  publication, timeout recovery and no automatic helper replay.
- Live recovery consumed review-ffc5c5a8c3e748e4982fb2f13968a4a1 from its existing
  result.json, preserving all four negative image verdicts. Six short criterion
  observations remained unresolved. One sufficiently detailed negative review
  resolved an existing criterion to FAIL, changing totals from14 FAIL/7 unresolved
  to15 FAIL/6 unresolved; this is new measured review evidence, not a native crash.
- Guard-row hash remained unchanged through recovery: **2 counted failures**,28
  failed jobs preserved, epoch2, limits6/source20/total. No native job submitted.
- No pending workflow/native jobs remained before launch. The checked continuation
  binds the current source2b37b77ce016462c943a217f67fb9418, native/report/validator
  hashes and unchanged complete guard history.

Snapshots under before/ and controller/attempt/plan receipts preserve the stopped
state. recovery-status.json records the actual repaired machine state. The user
authorized a fresh coding session to avoid the prior model's mistaken belief that
MCP review/status tools were permission-denied. Asset acceptance remains incomplete.

Monitor with `python3 scripts/run_bowling.py --status`. Automatic reconciliation
does not restart the coding controller after an unrelated STOP or acceptance stall.
