# Fresh-trial worker guide

Use bowling-blender52 only. The selected trial is
bowling52-qwen38-turbo-20261025-r1; runtime is Blender5.2.3 LTS on Z6, CPU only.
The queue is distinct from all retired trials, with an empty active guard DB.

Call blender_capabilities and blender_workflow_status. Use blender_api_lookup for
the installed API/return types. Stage00 starts empty only after reference review.
Later author edits use the current completed source. Poll all accepted native,
view- and review- IDs. Checkpoint/validation/ledger publication is automatic.

No inline rendering or output subdirectories. Use blender_render_view for actual
queued PNGs; fixed pixel-review and export/reimport tools gate acceptance/delivery.
API mistakes are soft only when verified by runtime/source evidence. Geometry
failures, arbitrary Python errors, cancellations and uncertain work remain hard.
Limits6 hard/source20 total; two current hard failures without asset advancement
stop the client. Never bypass STOP, replay identical failures or release leases.

The fixed validator and hash-verified installed API catalog are retained tooling,
not old asset geometry. All older scripts, native assets, references, downloaded
artifacts and controller databases were moved into the retired trial archive.
