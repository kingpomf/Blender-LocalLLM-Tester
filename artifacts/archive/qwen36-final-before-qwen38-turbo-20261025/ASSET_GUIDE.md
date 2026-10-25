# BowlingPair01 Asset Guide

## Geometry Summary

### Scene Structure
- **Root**: BowlingPair01_ROOT
- **Collections**: BP01_BALLS, BP01_COLLISION, BP01_PINS, BP01_PRESENTATION, BP01_STATIC

### Lane Surfaces (Stage 01)
- `Lane_L_Surface`: center X=-0.95m, Y=9.6m, top Z=0.0m
- `Lane_R_Surface`: center X=+0.95m, Y=9.6m, top Z=0.0m
- Width: 1.067m each (spec: 1.0668m ±0.005m)
- Span: Y=0 to Y=19.20m
- Approach surfaces: `Approach_L`, `Approach_R` from Y=-4.572 to Y=0

### Gutters and Collision (Stage 02/06)
- Four collision gutters in BP01_COLLLECTION: `COL_Gutter_L_Outer`, `COL_Gutter_L_Inner`, `COL_Gutter_R_Inner`, `COL_Gutter_R_Outer`
- Each gutter: 0.25m wide, 19.2m long
- **Note**: Visual gutters show flat profile (0.03m height). Collision meshes use simplified flat boxes.
- Central divider: `Divider_Cap` pieces

### Pin Decks (Stage 03)
- 20 pins total: `Pin_L_01` through `Pin_L_10`, `Pin_R_01` through `Pin_R_10`
- Pins use `Mat_PinWhite_Corrected` and `Mat_PinRed_Corrected` materials
- Pin tops at approximately Z=1.076m

### Bowling Balls (Stage 04)
- `Ball_01`: center at X=-0.221, Y=-2.30, Z=0.226 (on cradle)
- `Ball_02`: center at X=+0.221, Y=-2.30, Z=0.226 (on cradle)
- `Ball_03`: center at X=+0.663, Y=-2.30, Z=0.226 (on cradle)
- Ball radius: 0.108m, ~1100 vertices each
- **Known**: Ball_03 nearest rack distance is 0.447m (outside 0.005m contact spec)

### Alley Dressing (Stage 05)
- **AlleyFloor**: 78m wide, 338m long, 0.65m tall. Top surface at Z=0. Center: Y=10m
- **MaskingWall**: 12.5m wide, positioned at Y≈19.8m, bottom at Z=1.676m
  - **Fixed**: Was at Z=-0.144 (below pins), moved to Z=3.551 (bottom at Z=1.676)
- **Hood_Canopy**: 0.8m wide, 4.0m deep, at center X=0, Y=-2.15, Z=2.0
  - **Fixed**: Resized from 0.9m to fit within X=[-0.4, 0.4] bounds
- **Return Rack**: `ReturnRack_Cradle_0/1/2` support structure at Y=-2.3
- **Scoreboards**: `Scoreboard_L` and `Scoreboard_R` with screen panels
- **Benches**: `Bench_L` and `Bench_R` behind approach area
- **Decorative**: `LightBar_01`, `Stripe_01` wall panels

## Materials
- `Mat_Wood.001`: Lane surface wood
- `Mat_PinWhite_Corrected` / `Mat_PinRed_Corrected`: Pin body and stripes
- `Mat_Ball_01/02/03`: Ball finishes
- `Mat_Hood`: Return rack and hood metal
- `Mat_Wall`: Masking wall surface
- `Mat_Alfloor`: Alley floor

## Camera Positions (Presentation)
- **Overview**: Location [3, 8, 5], rot (68.8°, 0°, -17.2°) — looks down at full alley
- **Player**: Location [-1.5, 2, 1.5], rot (74.5°, 0°, 5.7°) — from approach toward pins
- **PinDeck**: Location [0, 10, 4], rot (80.2°, 0°, 0°) — behind pins looking forward
- **Props**: Location [0.5, -1.5, 1], rot (57.3°, 0°, -5.7°) — close-up of return/balls

## Import Notes
- All geometry uses metric units (1 Blender Unit = 1 meter)
- Origin at center of lane pair, Z=0 at lane surface level
- Y increases toward pin deck, X spans left(-) to right(+)
- Presentations objects in BP01_PRESENTATION collection are excluded from GLB exports
- Collision meshes in BP01_COLLISION collection use simplified flat geometry

## Validation Status
- **PASS**: Stages 00-03 (parsing, lanes, gutters, pins)
- **UNRESOLVED**: Ball grip socket visual proof (S04), return opening/scoreboard/masking labels (S05), normals documentation (S06)
- **FAIL**: Ball_03 rack contact (0.447m gap), gutter/lane collision profiles (flat vs concave), camera frustum framing, visual review evidence
