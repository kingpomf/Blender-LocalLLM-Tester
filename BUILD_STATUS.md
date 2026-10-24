# BowlingPair01 Build Status

- Status: NOT_STARTED
- Next stage: 00 — Contract and scene safety
- Active source job: none
- Accepted job IDs: none
- Default model: `z6-llama/qwen36-35b-a3b-mtp-q8` — current native 262,144-token context
- Actual model used: none — fresh trial has not started
- Execution host: Z6, MCP `bowling-blender52`
- Runtime: Blender 5.2.3 LTS; CPU rendering
- Trial queue: /home/kingpomf/Development/blender-new-llm-setup/var/bowling52-qwen36-mtp-q8-20261023-r2
- Operator intervention: fresh retry authorized after wrong-model startup; failed controller/session and guard archived, no accepted asset/image jobs
- Trial mode: continuous stages00–09; automatic compaction/pruning ON;16,384-token reserve; no configured step cap
- Active checkpoint: none
- Reference phase: NOT_STARTED — create imageMCP references before Stage 00
- Pending reference job: none

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

Fully quit and restart OpenCode in this checkout, then run `/bowling-run` once.
The launcher and both working phases are pinned to Qwen3.6 MoE. The fixed image
description tool provides pixel observations without replacing the trial agent.
Ordinary startup errors receive bounded diagnostic repair turns. Check progress with
`python3 scripts/run_bowling.py --status`; do not launch duplicate controllers.
Verify runtime identity and the fresh queue through `bowling-blender52`
capabilities, then run `python3 scripts/check_resume.py`. Begin Stage00 from an
empty scene, omitting source_job, and continue through delivery automatically.
Update both ledgers after accepted submissions, results and each passed stage;
compact when needed and resume from the saved verified source.

## Preserved history

The failed startup using Qwen3.8 is preserved at
`artifacts/archive/qwen38-startup-failed-20261023/`, including original controller
events/state, guard and pre-fix configuration. No image or Blender job was accepted.
This fresh r2 queue has no source, pending job, accepted job or reused stage PASS.

The previous Nemotron trial's original ledgers, scenes, scripts, downloaded
artifacts, configuration and guard database are preserved with a SHA-256
manifest at `artifacts/archive/nemotron-final-before-qwen36-2026-10-23/`.
All five accepted jobs were confirmed terminal remotely before archiving;
the locally queued entry was already completed remotely. No old source or
stage PASS carries forward. Earlier archives and remote queues remain evidence.
Infrastructure qualification uses its separate existing queue and does not
consume this fresh trial's guard budget. Model smoke tests are infrastructure
checks, not BowlingPair01 stage acceptance.
