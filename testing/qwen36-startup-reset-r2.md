# Qwen3.6-only agent startup repair and fresh r2 trial

## Observed failure

Failed session `ses_e94a30acdffers0uemKCUrSUw8` selected Qwen3.8 because the
controller and reference command explicitly hard-coded that primary model.
Its compound discovery command included an unapproved echo/redirection; the
headless CLI auto-rejected permission. The agent loop ended and the controller
immediately declared reference preparation failed instead of offering diagnosis.

No image generation or Blender authoring tool was called. The durable Blender
guard was empty; no reference manifest existed. The original controller PID was
gone and its lock was available before the authorized reset.

## Repair

- Launcher, Build agent, main/helper metadata and both phase commands pin
  `z6-llama/qwen36-35b-a3b-mtp-q8`. The retuned native262144 backend is preserved.
- No Qwen3.8 primary/agent phase remains. A fixed `review_reference_images.py`
  image-only API helper describes pixels using the existing vision model;
  Qwen3.6 owns planning, image prompts, design guide and Blender implementation.
  That helper checkpoints request state, reuses completed reviews and refuses
  uncertain replay. It cannot author or execute Blender code.
- `continue_loop_on_deny=true` lets the agent choose an allowed alternative to
  a denied optional tool. It does not grant the denied command permission.
- The controller allows at most two diagnostic repair turns for ordinary
  incomplete startup/validation, in the same phase session. It supplies actual
  tool errors/checker findings and instructs recovery of existing accepted IDs.
- Actual tool STOP/circuit-breaker, explicit interruption, transport uncertainty,
  BLOCKED/FAIL ledgers and exhausted repair budgets still stop immediately.

## Reset

Original events/state, empty guard and pre-fix files are hash-archived at
`artifacts/archive/qwen38-startup-failed-20261023/` (18 files at reset). Raw event
logs/databases stay local. New trial queue:
`var/bowling52-qwen36-mtp-q8-20261023-r2`.
Controller is not_started, guard empty, reference phase and all ten asset stages
NOT_STARTED; no source/pending/accepted jobs carry over. Historical archives remain.

## Verification

- **45 project tests pass**, including startup-repair continuation, hard-stop refusal,
  bounded no-progress recovery and exact Qwen3.6 model selection for every command.
- Project Pyright and git whitespace checks pass.
- Fresh installed config/MCP check confirms Qwen3.6 main/helper/Build/all commands,
  native256K, compaction/pruning enabled,16K reserve, no step cap, actual Blender
  5.2.3 and fresh r2 queue/guard. imageMCP still discovers both installed workers.
- Actual headless Qwen3.6 session `ses_e94944c91ffeS3jV4Qh5bI01Xj` attempted one
  deliberately unapproved harmless echo, received the auto-denial, continued with
  Read, and returned `QWEN36_STARTUP_RECOVERY_OK`. No build/image jobs submitted.
  Evidence is under `.runtime/startup-verification/`.
- The image-only helper was exercised separately against three existing image
  qualification fixtures. Actual pixel-derived JSON observations passed the full
  reference checker, without populating the fresh asset trial. Evidence is under
  `.runtime/vision-helper-verification/`.
- A normal authenticated request restored Qwen3.6 after helper verification.
  No runtime retune, lease release or service-control override was performed.

Retry: fully quit/restart OpenCode, open a **new** project session, confirm
Qwen3.6 35B A3B MTP Q8 (256K), then run **`/bowling-run`** once. Do not resume
the archived Qwen3.8 conversation. The actual asset trial has not been started.
