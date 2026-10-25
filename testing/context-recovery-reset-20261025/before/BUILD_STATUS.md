# BowlingPair01 — fresh Qwen3.8 Turbo trial

- Operator intervention: Fresh Qwen3.8 Turbo trial; previous asset and sessions archived; installed API/workflow tooling retained
- API corrections: 1 recoverable API errors excluded from hard-failure budget; original jobs preserved
- Operator validation pending: none
- Validation state: completed current-source measurements; see artifacts/reports/validation.json
- Checkpoint SHA-256: 38411b0cf6add697e68d6f1ef9a507ab5c6dd230cd4b6f7fcc31c4a6fb7f496b
- Workflow operation: inspect
- Status: BLOCKED
- Next stage: 00 — Contract and scene safety
- Active source job: c3e6eb270cce4cdd82671452900849bc
- Accepted job IDs: 819f4da4cd034d63b8de3d667da26918, fc2f201ee2df474f91fa719cc444aa3b, 01a404afb814410694570f67fc56f92d, 555107d2be954bedae6238e79d672d2e, 458cb411bcf04fc98150e7c8a8051725, 4b0c82d346e444f598aa5168538d0609, 3a633b9f15364f2dbc8f6ed09875d3e2, f8b997489e14416e9e982e4e2a09a8ae, 0365f115ad5142a1adfcb8daa56e774b, 228b7a9ea18b44b4a2eb80a886c78f70, c0f1ebc6e87b46eaa20ad4219f93803a, cc8a77a833294100bf565fa52a90f4e2, 4c86b26d25a34aefa3c5ac1a9c14e5e0, 75d5a46f1df14d9a9a007d57b81da328, f00a00ca8ba6463085397f8f8c530112, b09657773a0940bb892f7e4569380fdc, d9766279c8854861881167526fd69cc3, d5a8cbf0b0c842d28c023258bc457621, e4d04120abcc4a56b875da26b82a163e, 0198cc81ba674dd4a0b361d4c78a5ade, ee1a86a958a74ea697e3b318431bed95, 7324f5dc02f94af389dd34c88b8d05a8, ebdc369c87424a35b7dae8c2d8eecf99, 859248bde5f741b0abb2bf8d68b27cd5, b4016e83a51e4e538222ceadaa028a02, a5fa31912f8a41c681ad84b04c93300b, 8f57216693bf425db3fd52a9755bfb04, 14c9dac0210342218e96834ad16501b0, f664d018a7e94a6990f23949cf2158b8, 20f18ccf6c014fe0838e1d0f26ed9f1e, 774f0a6098004b8cb9fb73322c2bcae8, 273f82c414f0452d8c2ffd89424d689d, 4e31baaf40e44ac9b9e135b5a22ed469, 23154eb4d49d489e98dae186d8bde36b, c298305d64254bec8f1d314270c2af3f, 790cfa10b5474e18a0ae74a40955235b, c3e6eb270cce4cdd82671452900849bc, cf75e2259d47472bab2dfc2d4f7230cd, 2189c2862eae4906b957a35c80772426
- Default model: z6-llama/qwen38-turbo
- Actual model used: z6-llama/qwen38-turbo
- Trial queue: /home/kingpomf/Development/blender-new-llm-setup/var/bowling52-qwen38-turbo-20261025-r1
- Controller: STOPPED; awaiting explicit operator continuation
- Active checkpoint: artifacts/blend/BowlingPair01.blend
- Reference phase: READY
- Pending reference job: none
- Pending job: none
- Pending source job: none
- Failure budget: 6 per source / 20 total; current failures 4; 0 on current source; 5 historical failures preserved; reset epoch 0
- Next action: Read CONTROLLED_CONTINUATION.md and the active handoff report; repair Stage 00 and dependencies; use verified checkpoint tools.

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | FAIL | 1 failed/unresolved checks: S00_hierarchy; artifacts/reports/validation.json; validation job cf75e2259d47472bab2dfc2d4f7230cd |
| 01 | Lane pair and markings | FAIL | 6 failed/unresolved checks: S01_ArrowTri_L, S01_Dot_L, S01_Foul_L, S01_ArrowTri_R; artifacts/reports/validation.json; validation job cf75e2259d47472bab2dfc2d4f7230cd |
| 02 | Gutters, decks and pit | FAIL | 7 failed/unresolved checks: S02_Gutter_L_Outer, S02_Gutter_L_Inner, S02_Gutter_R_Inner, S02_Gutter_R_Outer; artifacts/reports/validation.json; validation job cf75e2259d47472bab2dfc2d4f7230cd |
| 03 | Reusable bowling pins | FAIL | 40 failed/unresolved checks: S03_Pin_L_01_red_bands, S03_Pin_L_01_closed_mesh, S03_Pin_L_02_red_bands, S03_Pin_L_02_closed_mesh; artifacts/reports/validation.json; validation job cf75e2259d47472bab2dfc2d4f7230cd |
| 04 | Reusable bowling balls | FAIL | 1 failed/unresolved checks: S04_ball_names; artifacts/reports/validation.json; validation job cf75e2259d47472bab2dfc2d4f7230cd |
| 05 | Return, seating and alley dressing | FAIL | 9 failed/unresolved checks: S05_return_bounds, S05_benches, S05_screen_bottoms, S05_masking_clearance; artifacts/reports/validation.json; validation job cf75e2259d47472bab2dfc2d4f7230cd |
| 06 | Materials, hierarchy and collision | FAIL | 10 failed/unresolved checks: S06_collision_triangle_budget, S06_collision_exclusion, S06_Gutter_L_Outer_collision, S06_Gutter_L_Inner_collision; artifacts/reports/validation.json; validation job cf75e2259d47472bab2dfc2d4f7230cd |
| 07 | Presentation cameras and lighting | FAIL | 9 failed/unresolved checks: S07_Overview_framing, S07_Overview_presentation, S07_Player_framing, S07_Player_presentation; artifacts/reports/validation.json; validation job cf75e2259d47472bab2dfc2d4f7230cd |
| 08 | Final measured validation | FAIL | Read-only validator completed: 138 PASS, 79 FAIL, 4 unresolved; source c3e6eb270cce4cdd82671452900849bc. |
| 09 | Export and delivery | NOT_STARTED | No qualified final export/round-trip delivery yet. |

## Next action

Read CONTROLLED_CONTINUATION.md and the active handoff report; repair Stage 00 and dependencies; use verified checkpoint tools.

## Evidence

Native and local measurements are in artifacts/reports/validation.json.
Historical ledgers, jobs, guard backups and operator assistance are preserved
under testing/. Only current measured PASS results may be carried forward.
