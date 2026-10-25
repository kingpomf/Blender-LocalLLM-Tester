# Kart01 — active simplified challenge

## BUILD

Construct one stylized low-poly kart from primitives or authored meshes. No imported kart, external image textures, or archived starting asset. X is width, Y length, Z up; front is negative Y. Use the dimensions in support/kart/helpers.py: maximum envelope 1.20 × 1.80 × 1.05 m; wheelbase 1.10 ± .02 m; front/rear tracks .92/.96 ± .02 m; wheel diameter .34 ± .01 m; width .14 ± .01 m; wheel bottoms Z=0 ± .01 m.

Create Kart01_Root at identity. All asset meshes belong to KART01_ASSET and descend from the root. Presentation belongs to KART01_PRESENTATION, outside the root. Mesh scale is identity; wheel spin axis is local X. No duplicate numeric suffixes or orphan meshes/materials. Total evaluated asset triangles ≤4500; separate per-component budgets are retired.

Required mesh names: Kart01_Chassis, Kart01_Floor, Kart01_Bumper_Front, Kart01_Bumper_Rear, Kart01_SidePod_L, Kart01_SidePod_R, Kart01_Axle_Front, Kart01_Axle_Rear, Kart01_Wheel_FL, Kart01_Wheel_FR, Kart01_Wheel_RL, Kart01_Wheel_RR, Kart01_Seat, Kart01_SteeringColumn, Kart01_SteeringWheel, Kart01_Pedal_L, Kart01_Pedal_R. Each wheel is one mesh with tire/rim material slots, avoiding alternate wheel hierarchies.

Use simple beveled pieces; a tapered nose, mirrored side pods, seat base/back silhouette, steering ring and two pedals must read clearly. Seat is centered in the rear half, pedals ahead and above the floor. Components must connect plausibly without deep intersections; wheels must clear the body. Chassis bottom ≥.17 m. Fine tread and mechanical detail are unnecessary.

Use Principled materials: MAT_Kart_Red (#C62828) for body/bumpers/pods; MAT_Rubber_Dark (#171717, roughness ≥.65) for tires; MAT_Rim_Silver for rims; MAT_Metal_Dark for axles/column/pedals; MAT_Seat_Black for seat/steering wheel. Every visible mesh including ground has a material. No external textures.

## REVIEW

Run support/kart/validate.py against the final scene. It covers objective scene checks; it does not certify subjective shape, support contact, color appearance, or visual quality. Review those separately and record each verdict. Do not label unmeasured requirements passed.

Use the fixed presentation rig and camera markers on frames 1–4: perspective, front, side, rear. Render actual scene at 512×512, check framing and visually distinct views. Presentation must not enter the asset export.

## DELIVER

Deliver artifacts/blend/Kart01.blend, artifacts/exports/Kart01.glb, artifacts/renders/Kart01_{perspective,front,side,rear}.png, artifacts/reports/validation.json, and artifacts/reports/BUILD_REPORT.md. Record model/Blender versions, supplied assistance, jobs, final dimensions/triangles, visual review, hashes, export settings and known defects. Export root and descendants only, with modifiers, materials and normals; document glTF axis conversion. Reimport GLB into an isolated scene and verify geometry/materials and absence of presentation. Complete only after all three phases pass.
