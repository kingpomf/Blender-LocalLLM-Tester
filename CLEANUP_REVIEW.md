# Retained Flash-Next trial — repository cleanup, November 13, 2026

This branch preserves the existing Flash-Next / EliteDesk trial source, accepted
submission snapshots, reference provenance, model-authored reports and completed
local ledgers. It does not start another trial or requalify the asset.

- All **127 tracked deletions** belong to the inherited template reset. Every
  deleted file was verified byte-identical to its copy under the ignored
  `.runtime/inherited-template/` archive. The published parent
  `94c7b4b0aaca66d32250f72db8ba4616eb98e5d2` also retains those files in Git history.
- Build/native exports, downloads, renders, runtime databases and logs remain
  local ignored artifacts. The pre-submission `pending-requests.json` draft is
  also ignored; accepted reference receipts and authored source remain tracked.
- **125 unit tests passed** using the existing worker Python environment.
  `tests/__init__.py` makes cross-test imports resolve to this repository rather
  than an unrelated installed `tests` package.
- Local reference integrity and resume-consistency checks passed. The recorded
  completed source is `17ade96359e8480cbe0472d26e87e495`, with no pending job.
  These are checks of retained receipts, not a fresh Blender render/asset review.
- Stale preflight/MCP text now reads the already-authorized failure limits from
  `submission_guard.py`; the limits and accumulated counters were not reset.

The current model-authored result is [BUILD_REPORT.md](BUILD_REPORT.md). Asset
acceptance, visual-review limitations and original job identities remain attached
to that historical trial. No controller, model, service or GPU job was launched
during this cleanup. Restart the trial's OpenCode/MCP session before using changed
tool descriptions; cleanup does not restart it automatically.
