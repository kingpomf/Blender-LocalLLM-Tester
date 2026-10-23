# BowlingPair01 Build Status

- Status: IN_PROGRESS
- Next stage: 04 — Reusable bowling balls
- Active source job: 196cdb8cfa614597a323a7669b7a28bc
- Accepted job IDs: 2b08a9f66e1f49debaa8a466b8e5ce56 (Stage 00), 13ca804e3a91441fb1545d9305e0e3f9 (Stage 01), 2773bdbdddbe4893be6dab21c629d14e (Stage 02), 196cdb8cfa614597a323a7669b7a28bc (Stage 03)
- Default model: `z6-llama/nemotron35-bolt-e4b` — 65,536-token context (selected 2026-10-23)
- Actual model used: retired Blender specialist in session ses_e9ab8bc15ffewRCFYXmdOPs5mK; Nemotron has not built any asset stages
- Execution host: Z6, MCP `bowling-blender52`
- Runtime: Blender 5.2.3 LTS, CPU rendering
- Trial queue: /home/kingpomf/Development/blender-new-llm-setup/var/bowling52-guarded-20261022
- Operator intervention: authorized fresh reset after unchanged-code loop; guarded toolchain installed; no bowling source or PASS reused
- Trial mode: automatic compaction/pruning OFF; maximum 60 agent steps per user turn; one stage per invocation
- Active checkpoint: none

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | PASS | scene.json, report.json, scene.blend (86172 bytes, sha256: 8d9aaa4b4f8a75cf2c1ed37e18da785d37b0e2826d8b51c3bdbee69a4144f25e) |
| 01 | Lane pair and markings | PASS | scene.json, report.json, scene.blend (96078 bytes, sha256: ae40f0175b212fea02c8258986c731f7c501a8e394df73a51f4ec6d72d4401b2) |
| 02 | Gutters, decks and pit | PASS | scene.json, report.json, scene.blend (99692 bytes, sha256: 86d8c20694878996081a3f918069b87a26a351d9d8fa68dbfaeb725d6d3c9557) |
| 03 | Reusable bowling pins | PASS | scene.json, report.json, scene.blend (104829 bytes, sha256: 61a1a6d8cb96c2b789147df51248692251f40d2b110cacd7cf2299b49348665b) |
| 04 | Reusable bowling balls | NOT_STARTED | |
| 05 | Return, seating and alley dressing | NOT_STARTED | |
| 06 | Materials, hierarchy and collision | NOT_STARTED | |
| 07 | Presentation cameras and lighting | NOT_STARTED | |
| 08 | Final measured validation | NOT_STARTED | |
| 09 | Export and delivery | NOT_STARTED | |

## Next action

Model replacement on 2026-10-23: the old weights and active model entries were
removed; Nemotron is selected for future evaluation. This existing run and its
exhausted guard budget are preserved, not reset. Historical Stage 01–03 PASS
claims were found unsupported during read-only review. Do not count these as
Nemotron results or attempt to bypass the stopped guard. An operator-authorized
fresh trial or measured repair plan is required before asset work resumes.

Restart OpenCode in this checkout and open a new session. Run `/bowling-start`.
First call `bowling-blender52` capabilities: require `runtime_verified=true`,
`actual_version="Blender 5.2.3 LTS"`, and the trial queue above. If this distinct
tool connection is absent, STOP and ask the operator to restart; never substitute
`z6-blender-worker`. Run `python3 scripts/check_resume.py`. Start Stage 00 from an
empty scene only while this trial is fresh. Complete and verify one stage, then
checkpoint and return to the user. On a tool STOP, report BLOCKED immediately.

## History and qualification

The previous trial (session ses_e9b45ccf7ffeWVraf3YntlLFE6) and local outputs,
original checkpoint ledgers, and prior tooling are archived at
`artifacts/archive/bowling-loop-2026-10-22/` with SHA-256 manifest. It ran on 4.5.14,
not 5.2, and repeated one identical Stage 03 submission 33 times. Historical PASS
claims are unverified. No archived script, scene, or job is this trial's source.

`testing/blender52-guarded/runtime-evidence.json` holds separate infrastructure
qualification jobs, including intentional failures. Their queue ends in
`-qualification`; they do not consume this trial's budget or count as stage work.
