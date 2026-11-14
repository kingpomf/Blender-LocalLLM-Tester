# EliteDesk worker flow

Use bowling-blender52 only, Blender5.2.3 LTS. The tool exposes the configured host,
CPU authoring and CUDA rendering. All source/camera/checkpoint IDs are local to
the EliteDesk CPU queue; rendered job IDs may have gpu- prefix. Keep host lineage.

Start with workflow_status, capabilities and targeted API lookups. New references
must pass before the first source-free authoring. Later edits use current source.
Poll every native/view-/review- ID. Checkpoints and measured ledgers are automatic.
Read compact scene_summary/validation_details, never entire scene/validation JSON.

Never render inline. Named views select cameras, enqueue shared CUDA work and
publish verified bytes from the same asset. Do not create a private GPU scheduler,
interrupt other GPU work or release leases. GPU failure diagnostics may require
operator log review; do not fetch completed artifacts from failed jobs.

Geometry/visual acceptance is distinct from execution success. Eight unchanged
validated revisions halt authoring for operator diagnosis. Preserve all budgets,
failed fingerprints, pending IDs and genuine STOPs. No arbitrary shell/delegation.
