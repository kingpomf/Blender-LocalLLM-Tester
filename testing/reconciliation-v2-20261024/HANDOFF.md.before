# BowlingPair01 — reconciled continuation handoff

- Run status: IN_PROGRESS
- Current stage: 01 — Repair lane markings; then02–04 before proceeding
- Last verified source job: d1ce998472c349ac9f9fc2775afefdf6
- Pending job: none
- Pending source job: none
- Latest verified local checkpoint: artifacts/blend/BowlingPair01.blend
- Checkpoint SHA-256: 4480223492c6790eceb0e66729cd5e99b15ee8875c25c45cfeab76af521bd017
- Next action: User invokes /bowling-continue; read CONTROLLED_CONTINUATION.md and testing/BALL_GENERATION_DIAGNOSTICS.md; repair01→02→03→04 from the completed source, then proceed through09.
- Reference phase: READY
- Pending reference job: none
- Trial queue: var/bowling52-qwen36-mtp-q8-20261023-r2
- Agent: z6-llama/qwen36-35b-a3b-mtp-q8; native262144 context and retuning preserved
- Failure budget: 6 per source / 12 total;6 prior failures retained,3 on current source
- Controller: STOPPED awaiting explicit operator continuation; no resumed generation submitted

The source is a completed, hash-verified repair base. Stage00 foundation checks
pass. Stage01–03 previously claimed passes were disproved by native read-only
audit4f572bf507534fe184d09d7014e0d60c; see the measured findings and report.
Stage04 has no successful ball revision. Its latest proposed operator is also
invalid in the actual Blender runtime. Do not accept code constants as geometry
measurements or substitute a failed job as the next source.

The user explicitly authorized reconciliation, diagnostic assistance and doubling
the failure limits. No geometry was repaired and no failure rows were deleted.
Record this as an assisted continuation, not a fresh unaided test. Pre-change
state and full job identities are retained in `testing/reconciliation-20261024/`.

Immediately save accepted IDs and pending state in BOTH ledgers before polling.
After terminal results, update the actual run/stage status, measurements, source,
canonical file and hash. Run `python3 scripts/check_resume.py` after every stage.
Use the exact permitted checker commands without `2>&1` or shell chains. A real
STOP still requires operator review; the increased limits are not unlimited retries.
