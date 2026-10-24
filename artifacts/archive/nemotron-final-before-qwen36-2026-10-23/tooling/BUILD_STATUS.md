# BowlingPair01 Build Status

- Status: NOT_STARTED
- Next stage: 01 — Lane pair and markings
- Active source job: none
- Accepted job IDs: edea3884aaac46a38cedf982b495193e, 9100c77e3e4d45b0b092ec6d6136e287
- Default model: `z6-llama/nemotron35-bolt-e4b` — 65,536-token context
- Actual model used: z6-llama/nemotron35-bolt-e4b
- Execution host: Z6, MCP `bowling-blender52`
- Runtime: Blender 5.2.3 LTS; CPU rendering
- Trial queue: /home/kingpomf/Development/blender-new-llm-setup/var/bowling52-nemotron-20261023
- Operator intervention: authorized fresh Nemotron reset on 2026-10-23; no old source, script or PASS reused
- Trial mode: automatic compaction/pruning OFF; 60 Build-agent steps per turn; one stage per invocation
- Active checkpoint: artifacts/blend/BowlingPair01.blend

## Stage ledger

| Stage | Name | Result | Evidence |
| --- | --- | --- | --- |
PASS
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

Fully restart OpenCode in this checkout, new session, select Nemotron 3.5 Bolt E4B
Q8 (64K), and run `/bowling-start`. Verify actual Blender 5.2.3 and the trial queue
above through `bowling-blender52` capabilities. Require no accepted/uncertain jobs
for this initial run. Run `python3 scripts/check_resume.py`. Begin Stage 01 using the last verified source (none) from
the empty scene with no source_job. Work one stage, measure acceptance, save the
native checkpoint and update both ledgers before returning. A completed job or
hardcoded passed=true is not stage acceptance.

On any tool STOP, checkpoint and report BLOCKED. Do not bypass retry budgets or
use archived scripts as implementations. Nemotron model installation/smoke tests
are infrastructure evidence, not BowlingPair01 stage results.

## Preserved history

The final Blender-specialist 5.2 run, original ledgers, native checkpoint,
scripts, downloads and exhausted guard database are preserved with SHA-256
manifest at `artifacts/archive/blender52-specialist-final-2026-10-23/`.
Its Stage 01–03 PASS claims were unsupported; none carries forward. Earlier
attempts remain under `artifacts/archive/`. The old remote queue is preserved.

Infrastructure qualification remains in a separate queue ending
`bowling52-guarded-20261022-qualification`, with evidence under
`testing/blender52-guarded/`. It does not consume the new trial's guard budget.
