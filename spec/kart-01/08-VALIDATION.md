# Stage 08 — Final Validation

Run deterministic Blender Python checks and save the script as `artifacts/scripts/validate_kart01.py`. Write machine-readable results to `artifacts/reports/validation.json` and a concise human summary to `artifacts/reports/BUILD_REPORT.md`.

## Required checks

- All named asset, material, camera, and light objects exist exactly once.
- Exactly four required wheel objects exist.
- Asset envelope and ground contact meet Stage 01 tolerances.
- Wheelbase, tracks, wheel diameter, and wheel width meet Stage 01 tolerances.
- All asset objects are parented to `Kart01_Root`.
- Mesh scales are applied.
- Every visible mesh has a material.
- No forbidden duplicate suffixes exist.
- No asset/presentation collection membership violations exist.
- Total evaluated triangle count is `<= 4,500`.
- `.blend` saves successfully.
- All four render files exist and are non-empty.

Any failed check makes Stage 08 FAIL. Record expected and actual values; do not hide failures behind an overall average.

