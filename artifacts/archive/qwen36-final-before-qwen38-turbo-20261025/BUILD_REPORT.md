# BUILD REPORT — BowlingPair01

## Build Metadata
- **Asset**: BowlingPair01 (modular two-lane bowling pair)
- **Blender Version**: 5.2.3 LTS
- **Render Engine**: EEVEE (CPU)
- **Source Job**: 2b37b77ce016462c943a217f67fb9418
- **Checkpoint Hash**: 9ff9753dc34b0aa0f20512d39e7f3a8fd4b9f1a36d947b9dfeac7f3198819d6b
- **Build Date**: 2026-10-24

## Geometry Changes Applied

### Fixed Issues (6 geometry issues resolved)
1. **AlleyFloor dimensions** — Rebuilt from bmesh with correct span [78m × 338m × 0.65m]. Floor now covers approach (Y=-4.572) through pin deck (Y=19.20). Previously had Y=0.65m depth (only covering center of scene).
2. **MaskingWall position** — Moved from Z=1.731 to Z=3.551. Bottom surface now at Z=1.676 (pin tops ~Z=1.076 + 0.60m clearance). Previously at Z=-0.144 (below pin tops).
3. **Hood_Canopy sizing** — Resized from [0.9 × 4.5 × 0.18] to [0.8 × 4.0 × 0.18]. Now fits within spec bounds X=[-0.4, 0.4], Y=[-4.3, -0.3].
4. **Ball heights** — All three balls raised from Z=0.108 to Z=0.2255 for proper contact with cradle tops (Z=0.1175).
5. **Ball_01 rack contact** — Resolved (nearest distance within 0.005m spec).
6. **Ball_02 rack contact** — Resolved (nearest distance within 0.005m spec).
7. **Ball spacing** — Ball_01 at X=-0.221, Ball_02 at X=0.221, Ball_03 at X=0.663 (0.442m gap).

## Validation Summary
- **Stage 00-03**: PASS (parsing, lanes, gutters, pins)
- **Stage 04**: 3 UNRESOLVED (ball grip socket visual inspection via renders)
- **Stage 05**: 1 FAIL (Ball_03 rack contact at 0.447m), 3 UNRESOLVED (label evidence)
- **Stage 06**: 6 FAIL (gutter/lane collision profiles — flat geometry vs concave spec), 1 UNRESOLVED (normals documentation)
- **Stage 07**: 7 FAIL (camera frustum framing, visual review evidence)

### Failures: 14 | Unresolved: 7

## Remaining Geometry Issues

### Gutter/Lane Collision (S06 — 6 FAIL + 1 UNRESOLVED)
- All four gutters and two lane collision meshes show flat profile dimensions [0.25 × 19.2 × 0.03]
- Spec requires concave cross-section with trough bottom 0.08-0.12m below lane surface
- Fix requires recreating collision meshes with bmesh concave profiles
- Normals documentation also pending

### Ball_03 Rack Contact (S05 — 1 FAIL)
- Ball_03 at X=0.663, nearest rack distance 0.447m
- Outside 0.005m contact spec
- Ball is positioned outside return rack X bounds but within lane approach area

### Camera Framing (S07 — 7 FAIL)
- 4 views rendered (overview: 898KB, player: 979KB, pindeck: 972KB, props: 921KB)
- Visual review observations:
  - Overview: Ceiling/wall corner, pins barely visible
  - Player: Right lane visible, left lane obscured by wall
  - PinDeck: Left pins visible, right side obscured
  - Props: Beige wall/bar visible, no balls/racks visible
- Camera orientations need fundamental repositioning/reorientation

### Visual Evidence (S04/S05 — 7 UNRESOLVED)
- Ball grip sockets: Requires render-based inspection
- Return opening, scoreboard labels, masking labels: Require visual evidence

## Rendered Views
| View | File | Size | Resolution |
|------|------|------|------------|
| Overview | BowlingPair01_overview.png | 898KB | 1280×720 |
| Player | BowlingPair01_player.png | 979KB | 1280×720 |
| PinDeck | BowlingPair01_pindeck.png | 972KB | 1280×720 |
| Props | BowlingPair01_props.png | 921KB | 1280×720 |

## Delivery Status
- **EXPORT_DELIVERY**: Not ready — requires complete measured/visual acceptance
- **FINISH_DELIVERY**: Not ready — requires export/reimport proof and BUILD_REPORT/ASSET_GUIDE

## Progress Summary
| Metric | Initial | Current |
|--------|---------|---------|
| Validation failures | 20 | 14 |
| Geometry issues fixed | 0 | 7 |
| Stages PASS | 4 (00-03) | 4 (00-03) |
| Render views | 0 | 4 (all submitted, none accepted) |
| Documentation | 0 | ASSET_GUIDE.md, BUILD_REPORT.md |

## Next Steps Required
1. Recreate gutter collision meshes with proper concave profiles using bmesh
2. Fix gutter collision mesh positions to align within 0.01m of visible gutters
3. Reposition cameras for proper scene framing (renders show walls, not subjects)
4. Document normals orientation and static pivot points
5. Re-render after camera/geometry fixes
6. Run visual review and export delivery
7. Finalize with blender_finish_delivery
