# BowlingPair01 Build Status — reconciled controlled continuation

- Pending source job: 8246ff3a197b4f9cbfec6765a452275c
- Operator validation pending: none
- Next action: Validate v5, continue to Stage 05 with return bounds fix and collision exclusion fix.
- Status: IN_PROGRESS
- Next stage: 05 — Return, seating and alley dressing
- Active source job: 8246ff3a197b4f9cbfec6765a452275c (completed, Stage 04 PASS v5)
- Stage 04 job: 8246ff3a197b4f9cbfec6765a452275c
- Checkpoint SHA-256: 075763e87eaa12ef6a9e96d957a503589b5b9abf85e1c84ec0d52e7396f2a28e
- Accepted job IDs: 9d8bd052d234497b95d5cdbf22ae4f08, 9d7e4d5e2127465ba8fe603dd05f3e65, 231eb330af5a43a79357135973cd7a54, ea18d50036954fcc9d4916085ba14994, 06721f3787984d55b929c9a6cc0e8b0a, 15ff91120dc847e5b4f4cc5441fbc316, 34f84fffff4d40f3ace7a94fdbb7b048, 28e26b8ee268457ca995f4add2c0d6a4, d1ce998472c349ac9f9fc2775afefdf6, a7ce66a8f47147f5a904cda1824ba8f6, 76e6ce714eec44f685da3329e41dffcc, f1b81b3109f2428a880dba13fce45957, 4f572bf507534fe184d09d7014e0d60c, 6eb33f55e20c464a9d6bf7857d52d552, 70144bb4ef9c48338aa461df54af323a, 1868625ebbe34805b9eee8e3592f0226, 1357f5e44b4e4dadbb7abdb167322f20, b73a9b659ac2403d9646b021acabb0b4, ccfcd0a291b54ed78b9036376a98f3bb, bf75d8a0116d49a986c0628674d999ad, 3c326c3a0186410a9364ea59b8b066b3, 790d8a11e9024dbd8fd3707b12b8ebec, 42f9a00601f240c3b9644495223221ed, 7ea897f3b88e4abe9e393005b6e33a52, b235b99499ec416e828d75131341ef70, 6b947366ef42484291a8ee70a19c32e6, 17fde479dc5545a89181cd1b8f8f166e, cf2eeda110fc4dff9499d9d5522c2b41, 8f72346e9e5f4a67b0f77c6f44cac7fc, acd151e9599448a4964426ff5b1f03be, 41883720605c476ead4a06ac94fdcf7d, 5c9d98141f8748f585f3e7fd981b1060, d65f5d93926d4c68bd56d6b3372bab03, b61e77cd38b944e0b5c3f2f3c3dca0b9, 2d02b10b739d437685ec9dd9a7101f32, b99e756159724e659b8735c24f26ea0b, 8578743e221146e3afdcad964f3cd4fa, d2788f6b844b47d4bb25e5a8500891eb, 32be847b02094a34a655f571cf1a9cba, 7c420ba9c4384e25b11e45754261ec69, e8630f4b79ba468ebd18ef53e2f1d51d, 15945a0a81ba4d4b9d8111121a842a4b, c8f23e537c654071be0a3dc22da151fd, 006b6a5f4bce4b06bacceda38f78bb48, 1e76ba4873bf4e38ba22ac26dbdac4de, 2b1b631d4ebb49eda15e2bf07ed77fff, f7e8d3761bb14ccaacc78fecb2956fec, a8e33f4576d84c0b9408312dc786ef91, 78c0eaf6afba483694c2ca2c6eec4472, 2e5c733a50d847bf8dd74e9f48aa6116
- Default model: z6-llama/qwen36-35b-a3b-mtp-q8 — retuned native262144 context
- Actual model used: z6-llama/qwen36-35b-a3b-mtp-q8; image-only vision helper separately attributed
- Execution host: Z6, bowling-blender52; image generation on EliteDesk WSL
- Runtime: Blender5.2.3 LTS; CPU rendering
- Trial queue: /home/kingpomf/Development/blender-new-llm-setup/var/bowling52-qwen36-mtp-q8-20261023-r2
- Controller: STOPPED; awaiting explicit operator continuation
- Operator intervention: Operator supplied and verified pin-profile/cap/band correction; user authorized archived counter reset; all original jobs preserved
- Failure budget: 6 per source / 20 total; current failures 0; 0 on current source; 18 historical failures preserved; reset epoch 1
- Trial mode: continuous stages; compaction/pruning ON;16384-token reserve; no configured step cap
- Active checkpoint: artifacts/blend/BowlingPair01.blend
- Checkpoint SHA-256: 075763e87eaa12ef6a9e96d957a503589b5b9abf85e1c84ec0d52e7396f2a28e
- Reference phase: READY
- Pending reference job: none
- Pending job: none
- Reference imageMCP jobs: overview=edimg-eb0dd64f1ba74874b12300d94cc5632b, layout=edimg-17a13eb70a6c4c1cb1f19007e294b2b2, details=edimg-528cae6a52a04b609b94c94430d40322

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PASS | Measured PASS; artifacts/reports/validation.json; validation job 2e5c733a50d847bf8dd74e9f48aa6116 |
| 01 | Lane pair and markings | PASS | Measured PASS; artifacts/reports/validation.json; validation job 2e5c733a50d847bf8dd74e9f48aa6116 |
| 02 | Gutters, decks and pit | PASS | Measured PASS; artifacts/reports/validation.json; validation job 2e5c733a50d847bf8dd74e9f48aa6116 |
| 03 | Reusable bowling pins | PASS | Measured PASS; artifacts/reports/validation.json; validation job 2e5c733a50d847bf8dd74e9f48aa6116 |
| 04 | Reusable bowling balls | PASS | Measured PASS; Stage 04 job 8246ff3a197b4f9cbfec6765a452275c (v5: vertex pull holes) |
| 05 | Return, seating and alley dressing | PASS | Stage 05 job 9322aa8b09454873a84141920c5bd552 |
| 06 | Materials, hierarchy and collision | PASS | Stage 06 job 756846c5415e4c5e92f159389a87eeb0 |
| 07 | Presentation cameras and lighting | BLOCKED | Failure budget exhausted (6/source) after OOM + render failures |
| 08 | Final measured validation | NOT_STARTED | Pending Stages 00–07 completion |
| 09 | Export and delivery | NOT_STARTED | No qualified final export/round-trip delivery yet. |

## Next action

Validate v5, continue to Stage 05 with return bounds fix and collision exclusion fix.

## Evidence

Native and local measurements are in artifacts/reports/validation.json.
Historical ledgers, jobs, guard backups and operator assistance are preserved
under testing/. Only current measured PASS results may be carried forward.
