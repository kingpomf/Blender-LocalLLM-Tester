# Stage 09 — Export and delivery

## Required files

- `artifacts/blend/BowlingPair01.blend` — editable final scene, packed dependencies.
- `artifacts/exports/BowlingPair01.glb` — assembled visual pair only.
- `artifacts/exports/BowlingPin01.glb` — one upright pin, base pivot at origin.
- `artifacts/exports/BowlingBall01.glb`, `BowlingBall02.glb`, `BowlingBall03.glb`
  in the same exports directory — each single ball with center pivot at origin.
- `artifacts/exports/BowlingPair01_Collision.glb` — only static proxies at original placement.
- All four PNGs from Stage 07.
- `artifacts/reports/validation.json`, `BUILD_REPORT.md`, `ASSET_GUIDE.md`,
  `DELIVERY_MANIFEST.json`.

Export GLB in meters using the standard glTF axis conversion (glTF Y-up).
Selection must exclude cameras, lights, presentation-only ground/backdrops if
not part of the intended alley, and collision from visual exports. Alley floor,
masking wall, seats, return and scoreboards ARE intended visual assets. Preserve
names and separable pins/balls. No missing/external texture dependencies.

Round-trip every GLB in a disposable Blender scene/job. Measure imported world
bounds, object/mesh counts, material presence and root hierarchy. Confirm pair
dimensions, twenty separate pins, three balls and no collision/presentation
leakage. Verify standalone origins/units and collision-only membership. Account
for glTF axis conversion and Blender import representation explicitly. Do not
damage the final native scene to perform round-trip validation.

The manifest lists relative path, byte count and SHA-256 for every required
deliverable except itself, plus final source job, export jobs and render sources.
Verify downloaded hashes against worker manifests. Keep local authoring scripts.

`ASSET_GUIDE.md` documents axes, scale, overall bounds, naming, reusable assets,
pivots, materials, collision alignment, suggested dynamic colliders and engine
import notes. Distinguish render mesh and collider; do not claim gameplay has
been tested. `BUILD_REPORT.md` summarizes stage results, observed budgets,
export/round-trip evidence, visual limitations and actual model/interventions.

Finish with `python3 scripts/check_resume.py`, and keep both checkpoints current.
Mark COMPLETE only when all required checks and deliveries pass; setup or remote
execution success is not a build PASS. Do not commit or push the generated work
without operator approval.
