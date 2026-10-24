# Enforced MCP workflow repair

The user authorized moving critical workflow instructions into tools, resetting
active error counters with archives, committing/pushing and relaunching detached.

## Operational changes

- Common inline render calls (including common import/assignment aliases), output
  directories, wrong RenderSettings format fields, Clearcoat and calc_normals are
  rejected before a guard reservation/backend submission. Recoverable JSON includes
  corrective tool guidance; these mistakes consume no failure attempt.
- New MCP status/checkpoint/validate/render-view/publication tools manage source,
  canonical bytes, accepted IDs, fixed validation and deterministic ledger mirrors.
  A successful author job automatically checkpoints and queues validation when
  polled; the stage result comes from actual measured evidence, not author reports.
- View IDs durably chain camera selection and one real CPU render. Camera branches
  never replace the authoritative asset source. Images publish with verified hashes
  and same-asset lineage; later image review is separate from execution success.
- Fixed image-description helper runs asynchronously and uses actual pixels,
  current measured facts and the written import guide. It never runs a coding agent
  or repairs geometry. Its request/result receipts survive MCP process restarts;
  uncertain outcomes are not replayed.
- Fixed delivery export tool creates six selection-specific GLBs, reimports them
  and measures actual imported bounds/mesh roles/materials. Delivery completion
  requires current validation, reviewed current images, native export/reimport
  receipts and required documentation before generating a hash manifest/COMPLETE.
- The custom bowling-coder primary agent remains Qwen3.6 but has no Bash/Task tools.
  Managed ledger, receipt, validator, specification and runtime paths are edit-denied.
  Ordinary geometry scripts and delivery documentation remain editable.
- Capabilities report compact budget/pending state instead of dumping every historic
  failed author request into the model's context. Compaction resumes from MCP state.

These are reliability controls, not a sandbox against a malicious agent with host
access. They prevent the observed ordinary workflow mistakes and premature PASSs.
Underlying worker CPU isolation, version checks, admission, hashes and failure
history remain intact. No coding-runtime retune or GPU-policy change is included.
