# Guarded trial setup verification — 2026-10-22

## Review outcome

The reported looping run used the original 4.5.14 queue, not the installed 5.2
test queue. Its Stage 02 source was `d53cac634a2b41ab89dcc92b61fc4976`. Read-only
inspection counted 33 failed authoring submissions with identical original-code
SHA-256 `467adacc5f144499f50210e38a50f39389c110a2d00d8a5b678e23f3e40096b1`.
The code already assigned its mesh; its claimed mesh-assignment repair was not
a change. Crossed quad ordering, unshared vertices, floating base-origin pins,
missing parenting/materials and checks of constants instead of geometry are
visible in the preserved script. Historical stage PASS claims remain unverified.

## Installed-path evidence

`opencode mcp list` in a fresh process reports bowling-blender52 connected and
z6-blender-worker disabled. Fresh effective-config preflight verifies Build
steps=60 and the unique launcher. Actual capabilities report:

- runtime_verified: true
- actual_version: Blender 5.2.3 LTS
- binary: /home/kingpomf/Development/blender-new-llm-setup/tools/blender-5.2.3-linux-x64/blender
- root: /home/kingpomf/Development/blender-new-llm-setup/var/bowling52-guarded-20261022
- accepted jobs: zero; uncertain submissions: zero; failures: zero

No build job was submitted into that fresh trial queue. It is created lazily on
the first real submission. Read-only inspection found no queued/running jobs in
either prior Blender queue. No protected workload was interrupted.

## Checks passed

- `python3 -m unittest discover -s tests -v`: 19 tests, covering durable guard and
  resume evidence including restarts, concurrent requests and ambiguous replies.
- Worker Python `testing/blender52-guarded/test_runtime_identity.py`: 5 tests,
  including wrong binary/runner/source rejection and executing version assertion.
- `.venv/bin/pyright`: zero errors, warnings or informational diagnostics for the
  active project workspace. Historical model scripts were archived, not silenced.
- Actual OpenCode LSP positive fixture: empty diagnostics.
- `scripts/preflight_blender52.py`: actual runtime/effective config/catalog PASS.
- `python3 scripts/check_resume.py`: NOT_STARTED, Stage 00, no source/pending job,
  zero active artifacts and no consistency issues.
- Archive manifest: all 47 preserved files match byte counts and SHA-256 hashes.
- `git diff --check`: PASS for tracked changes.

Real MCP qualification jobs (all isolated from the build):

| Check | Accepted job |
| --- | --- |
| Author and export on 5.2.3 | b5439c6f94eb4e7c89708c1c3fe1e619 |
| Native reopen and GLB round trip | 6e512b2451434283a85903b1ccb284d4 |
| CPU render, visible blue triangle | 920eff70083b4875924b4b7de396b0da |
| Intentional failure 1 | 118da573c2004b21a9216c6d89e997ad |
| Intentional failure 2 | bbb100951893406289c7fb194c1b1e84 |
| Intentional failure 3 | bb231c85fac94893bfbbd0152b338837 |

The unchanged failed-code call and fourth changed attempt were rejected without
additional jobs. GPU selection was rejected by the CPU-only tool schema.
See runtime-evidence.json for manifests and hashes. Qualification was explicitly
resumed after a catalog-count assertion was corrected before its first submission;
no uncertain work was replayed.

## Limits and handoff

The tool guard is an accidental-loop control, not a shell-access security boundary.
OpenCode's step-limit setting was verified in effective config; its forced-stop
behavior was not tested by burning through a model session. Model behavior and
asset quality remain untested in the fresh run. CPU rendering only.

The user must fully restart OpenCode and create a new session to load the new
connection. `/bowling-start` advances one stage at a time. A missing uniquely
named connection or any tool STOP is a blocker, not permission to use old tools.
The old run and prior tooling are preserved under
`artifacts/archive/bowling-loop-2026-10-22/`. No old source, model script, or stage
PASS is reused. The reviewed setup is on project/bowling-alley-pair.
