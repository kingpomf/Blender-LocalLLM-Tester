# BowlingPair01 Design Guide — Qwen3.8 Turbo Trial

Trial: bowling52-qwen38-turbo-20261025-r1
Reference images generated via imageMCP (backend: elitedesk, model: qwen-image-2.1-q4, 512x512, 25 steps) and inspected by the qwen38-27b vision helper.

## Reference Images

### Overview — image-179073e5a20443842c15afb95e505a4fceeca1b43e3b0fb053be1c63b23b55c5.png
Observed: Wide, low-angle view of a stylized bowling alley with parallel wooden lanes, white pins with red stripes, gray gutters, and a central ball return tray holding a red ball. Dark seating, colorful balls, and two blue hanging screens in the background.

Useful construction features:
- Establishes the overall composition: two lanes side-by-side with approach areas, pin decks, and seating behind
- Ball return is positioned between approaches, consistent with the spec's centered return rack
- Overhead scoreboards shown as hanging screens above lanes
- Wood-toned lane surfaces with visible board grain variation
- Color palette: wood tones for lanes, dark gray for gutters, white/red for pins, colorful balls

Corrections to apply during construction:
- Image shows multiple lanes; spec requires exactly two lanes
- Screen colors (blue) are artistic; spec requires readable lane labels "01" and "02"
- Pin details are small; spec dimensions (0.381m height, 0.121m max diameter, neck < 65% of body) must be measured, not inferred

### Layout — image-38e22a73d6f3c31687e25383ddf8ce094d6d99b53ec24c44ab282a8b1a96a67b.png
Observed: Top-down, symmetrical technical view of lane assembly showing four vertical metallic lane sections separated by light wood panels, with a central gray return mechanism and small orange components, framed by white border and dark upper housing.

Useful construction features:
- Clear layout showing lane spacing and gutter placement on all four sides
- Central return mechanism positioning validated
- Symmetrical arrangement of the two-lane pair
- Visual separation of functional zones (lanes, gutters, return, approaches)

Corrections to apply during construction:
- Image shows four lane sections; spec requires two lanes with four gutters (inner pair shared)
- Metallic lane appearance is artistic; spec requires wood with board variation along Y
- Lane width (1.0668m), center X positions (±0.95m), and Y extents (0 to 19.20) must be built to spec dimensions

### Details — image-facbd9bddf762e2b184ab2060441c3aa81da76774cb5da8f067fa533958e9827.png
Observed: Close-up of gray ball return tray with blue, red, and green bowling balls, positioned beside a low-poly pinsetter and a cluster of white pins with red rings on light wood floor marked with dark lines and arrows.

Useful construction features:
- Ball colors validated: blue, burgundy/red, green/teal match spec requirements
- Ball return tray/cradle geometry supports multiple balls
- Lane markings (dark lines, arrows) visible on approach surface
- Pin silhouette with red neck bands confirmed
- Low-poly aesthetic matches the target art style

Corrections to apply during construction:
- Finger holes on balls must be actual open recess geometry (≥0.015m depth), not painted
- Pin neck ratio must be measured: <65% of maximum body diameter
- Ball diameter (0.216m) and pin height (0.381m) must be exact spec values
- Pin rack spacing: 0.3048m nearest-neighbor, sqrt(3)/2 × 0.3048m row separation

## Design Decisions for Construction

1. **Art Style**: Stylized-realistic low-poly with clean silhouettes. Avoid overly detailed textures; use flat colors with material variation (wood grain, glossy balls, matte pins).

2. **Modular Organization**: Separate object groups for lanes, gutters, decks, pins, balls, return, seating, scoreboards, and dressing. All descend from BowlingPair01_ROOT.

3. **Material Strategy**: Use Principled PBR values with embedded textures for required appearance features (wood grain, pin stripes, ball colors). Procedural nodes only for optional variation.

4. **Lighting**: Balanced indoor alley lighting. Avoid blown-out highlights on polished ball surfaces. Readable silhouettes from all four presentation camera views.

5. **Dimensions**: All measurements follow the spec tables exactly. Lane width 1.0668m, lane length 18.288m foul-to-headpin, approach 4.572m, pin deck coverage, gutter cross-section 0.08–0.12m below lane.

## Visual Inspection Limitations

- Generated concept images are design inputs only, not final evidence of constructed geometry
- Precise dimensions, counts, and clearances must be measured in Blender, not inferred from images
- Material appearances in images may differ from final PBR material results
- Image resolution (512x512) limits visibility of small details like arrow markings and pin band widths
