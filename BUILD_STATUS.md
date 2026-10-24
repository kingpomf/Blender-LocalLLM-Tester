# BowlingPair01 Build Status — reconciled controlled continuation

- Status: IN_PROGRESS
- Next stage: 01 — Repair lane markings; then repair stages02–04 in order
- Active source job: d1ce998472c349ac9f9fc2775afefdf6
- Accepted job IDs: 9d8bd052d234497b95d5cdbf22ae4f08, 9d7e4d5e2127465ba8fe603dd05f3e65, 231eb330af5a43a79357135973cd7a54, ea18d50036954fcc9d4916085ba14994, 06721f3787984d55b929c9a6cc0e8b0a, 15ff91120dc847e5b4f4cc5441fbc316, 34f84fffff4d40f3ace7a94fdbb7b048, 28e26b8ee268457ca995f4add2c0d6a4, d1ce998472c349ac9f9fc2775afefdf6, a7ce66a8f47147f5a904cda1824ba8f6, 76e6ce714eec44f685da3329e41dffcc, f1b81b3109f2428a880dba13fce45957, 4f572bf507534fe184d09d7014e0d60c
- Default model: z6-llama/qwen36-35b-a3b-mtp-q8 — retuned native262144 context
- Actual model used: z6-llama/qwen36-35b-a3b-mtp-q8; image-only vision helper separately attributed
- Execution host: Z6, bowling-blender52; image generation on EliteDesk WSL
- Runtime: Blender5.2.3 LTS; CPU rendering
- Trial queue: /home/kingpomf/Development/blender-new-llm-setup/var/bowling52-qwen36-mtp-q8-20261023-r2
- Controller: STOPPED; controlled continuation prepared, awaiting operator command
- Operator intervention: reconciled native scene/ledgers, supplied diagnostic report, doubled limits without clearing history; no geometry repaired
- Failure budget: 6 per source / 12 total;6 historical failures retained,3 on current source
- Trial mode: continuous stages; compaction/pruning ON;16384-token reserve; no configured step cap
- Active checkpoint: artifacts/blend/BowlingPair01.blend
- Checkpoint SHA-256: 4480223492c6790eceb0e66729cd5e99b15ee8875c25c45cfeab76af521bd017
- Reference phase: READY
- Pending reference job: none
- Pending job: none
- Reference imageMCP jobs: overview=edimg-eb0dd64f1ba74874b12300d94cc5632b, layout=edimg-17a13eb70a6c4c1cb1f19007e294b2b2, details=edimg-528cae6a52a04b609b94c94430d40322

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PASS | Native audit4f572bf507534fe184d09d7014e0d60c verifies metric units, five collections, identity EMPTY root and parent hierarchy; canonical checkpoint hash verified. |
| 01 | Lane pair and markings | FAIL | Native audit:30 markings at Z≈0.147–0.150 rather than within0.002 of lane surface. testing/BALL_GENERATION_DIAGNOSTICS.md section4. |
| 02 | Gutters, decks and pit | FAIL | Native audit: left gutters≈0.410m wide; inner gutter sections overlap lanes; left outer extent X=-1.8134. |
| 03 | Reusable bowling pins | FAIL | Native audit:18 pins advance toward-Y; no red-band faces; shared pin mesh has26 boundary/nonmanifold edges. |
| 04 | Reusable bowling balls | FAIL | Three failed jobs a7ce66a8f47147f5a904cda1824ba8f6,76e6ce714eec44f685da3329e41dffcc,f1b81b3109f2428a880dba13fce45957; no ball revision completed. |
| 05 | Return, seating and alley dressing | NOT_STARTED | |
| 06 | Materials, hierarchy and collision | NOT_STARTED | |
| 07 | Presentation cameras and lighting | NOT_STARTED | |
| 08 | Final measured validation | NOT_STARTED | |
| 09 | Export and delivery | NOT_STARTED | |

## Next action

Read `CONTROLLED_CONTINUATION.md` and `testing/BALL_GENERATION_DIAGNOSTICS.md`.
The user will invoke `/bowling-continue` (or the documented controller command).
Start from the completed, integrity-verified source above; it is a repair base,
not proof that Stage01–03 passed. Do not use the failed ball jobs or restart empty.
Repair01→02→03→04, remeasure each stage, then continue05–09 within the new budgets.

## Reconciliation evidence

`testing/reconciliation-20261024/` contains pre-change ledgers/controller, guard
backup, terminal remote job statuses, fetched artifact hashes, immutable submitted
ball-code snapshots, native read-only audit and measured findings. All13 accepted
jobs are terminal (7 completed,6 failed); no pending/uncertain submission exists.
The operator audit is not a new model-authored asset revision and is not the source
for continuation. Earlier PASS claims were corrected against actual scene data.

Previous trial archives remain under `artifacts/archive/`. The current failure
ledger and original scene/job artifacts are preserved; no limit history was reset.
