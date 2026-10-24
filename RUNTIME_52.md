# Guarded Blender 5.2 trial — fresh Qwen3.6 MTP Q8 evaluation, 2026-10-23

## Start

1. Quit the OpenCode process that ran the failed trial, not just its conversation.
2. Reopen `/Users/start/Development/Blender-LocalLLM-Tester`, new session, Build agent.
3. Confirm the MCP list has **bowling-blender52**, with the old **z6-blender-worker disabled**.
4. Run `/bowling-run` once for the automatic reference→coding workflow. Coding
   proceeds through all remaining stages without next-stage prompts. A STOP still
   requires operator review; inspect the controller status before resuming.

Optional operator preflight (no build submission):

```sh
/Users/start/Development/blender-new-llm-setup/.venv/bin/python scripts/preflight_blender52.py
python3 scripts/check_resume.py
```

## Runtime identity

- Official Blender **5.2.3 LTS**, build `e13b728c6880`.
- Z6 binary: `/home/kingpomf/Development/blender-new-llm-setup/tools/blender-5.2.3-linux-x64/blender`.
- Archive SHA-256: `78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec`.
- Official release: <https://download.blender.org/release/Blender5.2/>.
- Project stubs: **fake-bpy-module-5.2==20260730**, Pyright **1.1.414**.
- Selected agent for ALL phases: `z6-llama/qwen36-35b-a3b-mtp-q8`, native262,144 context. A fixed image-description helper invokes the vision API only for pixel observations; it never replaces the trial agent.
- Fresh trial queue: `/home/kingpomf/Development/blender-new-llm-setup/var/bowling52-qwen36-mtp-q8-20261023-r2`.
- Qualification queue: `/home/kingpomf/Development/blender-new-llm-setup/var/bowling52-guarded-20261022-qualification`; separate local state/downloads, unchanged historical fixture IDs.

The launcher pins host, binary and root directly; inherited environment values
cannot redirect them. Before every submission it runs the actual executable's
`--version` and checks any queue runner for a conflicting binary. Authoring also
asserts `bpy.app.version[:3] == (5,2,3)` in the executing sandbox. Completed
manifests and sources must report `5.2.3 LTS`. The fresh queue carries no 4.5 jobs.
Wrapped `author.py` executes the exact model code as `/job/submitted.py` for
traceback clarity; local saved scripts remain the model's original code.

## Enforced loop controls

`scripts/submission_guard.py` persists state in `.runtime/blender52/submissions.sqlite`:

- Hashes executable Python AST plus source/operation. Comment or whitespace edits
  cannot disguise an unchanged failed submission.
- Returns an existing completed result for an identical successful request.
- Rejects duplicate pending/failed requests and overlapping pending work.
- Refreshes accepted pending jobs before deciding, even if the model skipped polling.
- Rejects further submissions on a source after three failed/cancelled attempts;
  six failures across the trial stop all new submissions.
- Records a durable uncertain reservation before network submission. Lost replies
  block new submissions until an operator reconciles the exact accepted remote job.
- Rejects a silent empty-scene restart once an authored scene has completed.
- Process locking prevents concurrent clients from racing duplicate submissions.

Status, diagnostics and artifact access remain available. No model-facing reset
tool exists. This prevents accidental loops through this MCP; it is not a security
sandbox against an agent deliberately using shell/file access to bypass it.

The former Build-agent `steps=60` limit is removed. Automatic compaction and
pruning are enabled with a16,384-token reserve. Checkpoint every stage and before
compaction, then reread both ledgers and continue from the same verified source.
Built-in doom-loop permission and persistent failure budgets remain enforced.
The controller automatically continues verified stage advances and allows up to
two diagnostic recovery turns for ordinary incomplete startup/validation. It
stops on BLOCKED/FAIL, explicit STOP, transport uncertainty or exhausted recovery.
It does not reset guards or blindly replay accepted jobs.

## Catalog and rendering

Only nine tools are advertised: capabilities, author, inspect, export, render,
status, diagnostics, cancel and artifact fetch. The render schema accepts CPU only.
Use individual review frames and bounded samples within existing worker limits.
The shared GPU renderer remains on 4.5; no shared gateway, leases, default runtime
or other project configuration is changed.

## Evidence and reset

`testing/blender52-guarded/runtime-evidence.json` records real 5.2.3 authoring,
native reopen, GLB round trip, CPU rendering, terminal diagnostics, semantic
duplicate rejection and the three-failure cutoff. The guard regression tests
also exercise restart persistence, lost replies, concurrency, fresh-restart
prevention and aggregate limits. Positive/negative LSP fixtures remain under
`testing/blender52/`. They are infrastructure fixtures, not model-authored assets.

The failed session `ses_e9b45ccf7ffeWVraf3YntlLFE6` actually used the original
4.5.14 queue. Read-only queue inspection found 33 failed author submissions with
identical code hash `467adacc5f144499f50210e38a50f39389c110a2d00d8a5b678e23f3e40096b1`
from source `d53cac634a2b41ab89dcc92b61fc4976`. Why its process retained/selected
the old connection was not established; the new server identity makes this mismatch
visible. It must not be reported as a 5.2 model result.

The earlier loop and pre-reset tooling were archived with hashes at
`artifacts/archive/bowling-loop-2026-10-22/`. The final 5.2 old-model attempt,
active output/scripts/ledgers and exhausted guard are now preserved at
`artifacts/archive/blender52-specialist-final-2026-10-23/` for the authorized
Nemotron reset. Native scenes/job data/guard databases may
be Git-ignored, so the local archive is more complete than Git. Old remote queues
are preserved. No historical source, implementation or PASS is reused. All ten bowling stages
are NOT_STARTED; infrastructure fixtures were run only in the qualification queue.

The subsequent Nemotron trial is now archived at
`artifacts/archive/nemotron-final-before-qwen36-2026-10-23/`, with original
ledgers, all active artifacts, guard database and SHA-256 manifest. Its five
accepted jobs were terminal before reset (four completed, one failed).
The operator explicitly authorized the new Qwen3.6 MTP Q8 trial. The new queue
and empty local guard reuse no historical scene, script or stage result.

## Operator recovery

After a breaker stops the run, review diagnostics, code differences and accepted
IDs. For an uncertain submission inspect the remote queue before doing anything
else; never delete the reservation and blindly resubmit. There is deliberately no
automatic replay or guard-clear command. An explicitly authorized new trial gets
an archived ledger and a new queue identity, rather than rewriting prior evidence.

For configuration rollback, preserved pre-guard files are in the archive's
`tooling/` and `opencode.json`. Restart OpenCode after any config-time changes.
Do not point new 5.2 scenes at 4.5 or treat its old source IDs as current jobs.
