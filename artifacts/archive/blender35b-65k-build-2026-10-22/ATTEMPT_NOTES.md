# Last 65K build — archived for 100K reset, 2026-10-22

This archive preserves all local attempt directories, scripts, native checkpoint,
downloads, and setup snapshots before resetting the test. Model:
`z6-llama/qwen38-blender-35b`, then configured at 65,536 tokens.

The ledger was stale: it still declared NOT_STARTED, no active source and no
accepted jobs, while its stage table claimed Stage 00 PASS for
`b1ca46e6407c432294ee33a73fdf23ac`. Scripts existed through Stage 07 and final
validation, along with a local Kart01.blend and metadata from 10 downloaded jobs.
These filenames do not establish stage completion. No unverified PASS is carried
forward, and this reset did not attempt to certify the old asset.

The user requested a fresh test after raising context to 102,400. The new run has
a separate HANDOFF.md and read-only resume consistency preflight. Later sessions
must reconcile existing work rather than trust a stale NOT_STARTED header.
