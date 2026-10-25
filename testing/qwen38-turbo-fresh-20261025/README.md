# Clean Qwen3.8 Turbo project reset

The user explicitly requested resetting the entire active project and starting
over with qwen38-turbo while retaining lessons from previous failures.

## Isolation and preservation

Retired model/trial: z6-llama/qwen36-35b-a3b-mtp-q8 /
bowling52-qwen36-mtp-q8-20261023-r2. Its **108 accepted attempts and33 failed jobs**,
original guard databases, failure classifications/reset history, coding/reference
sessions, event logs, authored scripts, native assets, exports, images, receipts,
design guides and reports are preserved under:
artifacts/archive/qwen36-final-before-qwen38-turbo-20261025/.
ARCHIVE_MANIFEST.json journals the move and retained tooling hashes. No attempt,
failed request fingerprint or prior evaluation evidence was deleted.

The new trial is **bowling52-qwen38-turbo-20261025-r1**: isolated remote queue,
new local guard/workflow/controller state, no source/checkpoint, no asset scripts,
no reference images, no accepted stages, zero failures. Retained immutable tooling
is the native validator and hash-verified installed API/return-type catalog. They
are not old asset inputs. Specifications and hardened workflow code are retained.

## Model and workflow

The installed gateway advertises **z6-llama/qwen38-turbo** enabled. Project config
and all four command profiles select that model for both reference planning and
coding. Context139264/output16384, compaction/pruning enabled with16384 reserve,
no configured step cap. Fixed pixel-only helpers remain separately attributed.

Fresh concepts are generated first through imageMCP/EliteDesk Q4 and verified
receipts/pixel review, then a separate new Turbo coding session builds Stage00.
No retired scene or manual pin repair is inherited. API lookup, source-proven
soft errors, hard-error limits, actual geometry/visual acceptance, automatic
review reconciliation and selected export/reimport checks remain in force.
Current instructions explicitly require single-group edits, valid curve endpoints,
consistent local/world transforms and correct collision collection membership.

## Verification

- **112 unit tests pass**, targeted Pyright clean.
- Effective-config/MCP preflight selects qwen38-turbo, actual Blender5.2.3 LTS,
  CPU-only new queue,18 workflow tools, zero accepted jobs/failures.
- Fresh-state consistency accepts immutable tooling while still rejecting any
  old asset validation report or other active output.
- Empty-workflow status cannot falsely attempt delivery completion when both
  source and delivery are absent; a new regression covers this previously hidden bug.
- `prelaunch.json` records a fresh actual MCP status/API/capability handshake,
  retained tooling hashes, model discovery and proof of no old asset/session state.
- Historical pin-payload regression now reads the archived payload; it is not an
  active source file for the new model.

Use `python3 scripts/run_bowling.py --status`. A detached launch is not proof of
asset acceptance. Fresh process/session activity must be checked separately from
read-only model discovery. Existing interactive OpenCode processes require restart
to load the changed model/configuration. No GPU leases or runtime tuning were
manually changed; the gateway handles requested model admission normally.
