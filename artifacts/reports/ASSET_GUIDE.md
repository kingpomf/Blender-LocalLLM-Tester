# BowlingPair01 Asset Guide

## Coordinate system and units

- Blender units are metric with `unit_settings.scale_length = 1.0`.
- One Blender unit equals one meter.
- The asset uses a Y-forward alley axis, X lateral axis, and Z up axis.
- The scene root is `BowlingPair01_ROOT`, an empty at the world origin.
- The glTF delivery pipeline uses the standard glTF Y-up axis conversion during export.

## Major collections

- `BP01_STATIC` contains the fixed pair structure, gutters, decks, pit, floor, wall, seating, return, screens, score grids, digits, decorations, and rails.
- `BP01_PINS` contains twenty separate pin objects with base pivots.
- `BP01_BALLS` contains three separate bowling-ball objects with center pivots.
- `BP01_COLLISION` contains hidden collision-only static proxies.
- `BP01_PRESENTATION` contains the four required cameras and lighting helpers.

## Approximate scene envelope

The current visual pair is designed as two adjacent bowling lanes with approach, lane, pin deck, pit, masking wall, return rack, and score/masking labels.

Measured design envelope for the visual static geometry:

- X lateral: about `-2.20 m` to `+2.20 m`
- Y forward: about `-7.00 m` to `+21.05 m`
- Z vertical: about `-0.32 m` to `+3.42 m`

The Y range covers approach floor, lane surface, pin deck, pit, and masking wall. The lower Z value is the pit floor depression; the upper value includes the masking-wall/overhead dressing geometry. Cameras and lights are presentation-only and are not part of visual GLB exports.

## Naming and hierarchy

All required asset objects use `BP01` naming discipline and are parented to `BowlingPair01_ROOT`.

Representative groups:

- Lane surfaces: `Lane_L_Surface`, `Lane_R_Surface`
- Approaches: `Approach_L`, `Approach_R`
- Foul lines: `Foul_L`, `Foul_R`
- Arrow markers: `ArrowTri_L_01` through `ArrowTri_L_07`, and the same R suffix
- Dots: `Dot_L_01` through `Dot_L_07`, and the same R suffix
- Gutters: `Gutter_*`
- Pin decks and pit: `PinDeck_L`, `PinDeck_R`, `Pit_Catch`
- Pins: `Pin_L_01` through `Pin_L_10`, and `Pin_R_01` through `Pin_R_10`
- Balls: `Ball_01`, `Ball_02`, `Ball_03`
- Return rack: `ReturnFrame_Post`, `ReturnRack_Tray`, and related `Return*` objects
- Screens and labels: `Screen_L`, `Screen_R`, `ScoreGrid_L`, `ScoreGrid_R`, `LaneDigits_L`, `LaneDigits_R`, `MaskingDigits_L`, `MaskingDigits_R`
- Collision proxies: `COL_Gutter_*`, `COL_LaneBed_L`, `COL_LaneBed_R`

## Pivots and reusable objects

- Pin objects use a base pivot at the object origin for upright standing placement.
- Ball objects use center pivots at their object origins.
- Standalone `BowlingPin01.glb` is exported from one reusable pin object and should retain the base-origin upright pivot.
- Standalone `BowlingBall01.glb`, `BowlingBall02.glb`, and `BowlingBall03.glb` retain center-origin ball pivots.
- The assembled visual pair excludes cameras, lights, collision-only proxies, and presentation helpers.

## Materials

Materials are Blender-native and use packed or procedural Principled BSDF setups. No external image-texture dependencies are required.

Material slots separate the major visual classes: lane surface, approach floor, gutters, rails, decks, pit, pins, balls, return rack, screens, scoreboards, masking wall, benches, and decorative light bars. Exported GLB files preserve material slots and object separation.

## Collision

Collision proxies live in `BP01_COLLISION`, are hidden from render, and are exported only through `BowlingPair01_Collision.glb`.

Included static proxies:

- `COL_LaneBed_L`, `COL_LaneBed_R`
- `COL_Gutter_*`

They are placed at original world coordinates and are intended for simple static lane/gutter collision. They do not represent gameplay physics, pin falling, ball motion, gutter ball routing, or collision response testing.

Suggested engine collision:

- Pins: use capsule or cylinder colliders approximating pin diameter and height, or use the exported pin visual mesh only if the engine’s dynamic collision is tested.
- Balls: use sphere colliders with radius `0.108 m`.
- Gutters: use the collision GLB proxies for gutter containment and lane-edge collision.
- Pin deck/pit: use simple box or height collision at the measured deck and pit surfaces.

## Import notes

- Import visual and collision GLBs separately.
- Do not treat `BowlingPair01_Collision.glb` objects as render geometry.
- Keep the root empty or import container at the world origin.
- Preserve the Y-forward/Z-up Blender convention in Blender; glTF importers will apply the Y-up conversion automatically.
- Keep pins and balls as separate transformable instances rather than baking them into the static pair.
- Verify imported dimensions after conversion: the full pair envelope should remain approximately 4.4 m wide, 28 m deep, and 3.7 m tall.
