# BowlingPair01 Build Status

- Status: NOT_STARTED
- Next stage: 00 — Contract and scene safety
- Active source job: none
- Accepted job IDs: none
- Default model: `z6-llama/qwen38-blender-35b` — 262,144-token context
- Actual model used: not yet recorded
- Execution host: Z6, MCP `bowling-blender52`
- Runtime: Blender 5.2.3 LTS, CPU rendering
- Trial queue: /home/kingpomf/Development/blender-new-llm-setup/var/bowling52-guarded-20261022
- Operator intervention: authorized fresh reset after unchanged-code loop; guarded toolchain installed; no bowling source or PASS reused
- Trial mode: automatic compaction/pruning OFF; maximum 60 agent steps per user turn; one stage per invocation
- Active checkpoint: none

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
| 00 | Contract and scene safety | NOT_STARTED | |
| 01 | Lane pair and markings | NOT_STARTED | |
| 02 | Gutters, decks and pit | NOT_STARTED | |
| 03 | Reusable bowling pins | NOT_STARTED | |
| 04 | Reusable bowling balls | NOT_STARTED | |
| 05 | Return, seating and alley dressing | NOT_STARTED | |
| 06 | Materials, hierarchy and collision | NOT_STARTED | |
| 07 | Presentation cameras and lighting | NOT_STARTED | |
| 08 | Final measured validation | NOT_STARTED | |
| 09 | Export and delivery | NOT_STARTED | |

## Next action

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
