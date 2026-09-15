# Stage 09 — Export and Delivery

## Export

Export only `Kart01_Root` and its descendants to `artifacts/exports/Kart01.glb`.

Use GLB settings suitable for Unity:

- Apply modifiers.
- Include materials.
- Include normals.
- Exclude cameras, lights, ground, and reference guides.
- Preserve Z-up source orientation and document any exporter axis conversion.

## Final report

Append to `artifacts/reports/BUILD_REPORT.md`:

- Model and Blender versions.
- BlenderMCP connection result.
- Stage-by-stage PASS/FAIL table.
- Final dimensions and triangle count.
- Exact artifact paths.
- Known defects or deviations.
- Export success and file size.

Set `BUILD_STATUS.md` to COMPLETE only if Stages 00–09 all pass.

