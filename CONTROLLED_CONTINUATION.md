# Current authorized continuation — API/accounting reset epoch3

The user authorized review/fixes, an archived reset of active failures to zero,
commit/push, and a fresh detached Qwen3.6 run. Read
`testing/api-accounting-reset-20261025/HANDOFF.md` for the current instructions.
Earlier plans are historical evidence, not active instructions.

- Agent/model: **bowling-coder / z6-llama/qwen36-35b-a3b-mtp-q8**; context262144,
  compaction/pruning enabled,16384 reserve, no step cap.
- Blender: **5.2.3 LTS**, same bowling-blender52 CPU-only queue.
- Starting source: **2b37b77ce016462c943a217f67fb9418**. MCP workflow status is
  authoritative if the source advances. Canonical native hash at authorization:
  **9ff9753dc34b0aa0f20512d39e7f3a8fd4b9f1a36d947b9dfeac7f3198819d6b**.
- New epoch3: **0 active hard failures,0 active API corrections,0 active streak**.
  All106 accepted attempts and31 historical failed jobs are preserved. Limits
  remain6 hard failures/source20 total. No further reset is authorized.
- References remain READY. Do not regenerate them or start with an empty scene.

Use blender_api_lookup for unfamiliar APIs and return types. Object.children is
a tuple; never call children.unlink. Use parenting/deletion APIs as the active
handoff explains. Preflight API feedback is recoverable; correct code and continue.
Runtime API errors are soft only when verified against the installed runtime and,
for builtin return types, the accepted source and exact failing traceback line.
Status and diagnostics agree on classifications. Old pre-reset failures cannot
recharge current counters. Identical failed scripts still cannot be replayed.

Make **one small criterion/object-group correction per revision**, then poll the
native job and its automatic validator. Preserve measured Stage00–03. Inspect
collision-only meshes instead of rebuilding valid visual gutters. Job completion
is not an acceptance PASS. Correct actual invalid geometry and camera occlusion.

Use named queued renders and fixed pixel-review tools. The earlier review is
completed and negative; it is not stuck or permission-denied. Automatic review
reconciliation remains active. Short criterion notes stay unresolved. Write
ASSET_GUIDE.md and BUILD_REPORT.md under artifacts/reports; export/reimport and
finish delivery only through the fixed tools after current acceptance passes.

No Bash/delegation, inline rendering, manual ledger/receipt edits, validator
changes or counter manipulation. Continue while making verified progress. A true
STOP, uncertain submission, hard-error circuit breaker or explicit user stop halts
the run. Re-query workflow state after compaction. Never relaunch a duplicate.

Operator monitoring: `python3 scripts/run_bowling.py --status`.
