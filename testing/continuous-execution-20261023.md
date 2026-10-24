# Continuous execution and compaction — 2026-10-23

User-authorized change: preserve the separately retuned native256K model, execute
stages successively without “next” prompts, and compact when needed.

- `compaction.auto=true`, `prune=true`, reserve16384; removed the build steps60 cap.
- AGENTS and `/bowling-start` now require all remaining stages through verified
  delivery, durable checkpoints after each stage and continued work after compaction.
- `/bowling-run` starts a background controller once: vision/reference phase,
  validated handoff, then a separate MTP coding session. Successful stage-boundary
  returns continue in that same coding session automatically.
- Controller retains session IDs/events under ignored `.runtime/autonomous-run/`.
  Duplicate controllers are locked out. BLOCKED/FAIL, client errors, inconsistent
  evidence and no verified progress stop instead of looping or clearing guards.
- Existing per-source/aggregate failure limits and explicit-stop behavior remain.
- `--status` is read-only. `--resume` is explicit after interruption/reconciliation;
  accepted image/Blender IDs are recovered from checkpoints rather than replayed.

Verification: fresh installed OpenCode config shows no build step cap and the
requested compaction settings. Real MCP handshakes still verify the fresh Blender
queue and both image backends. Controller tests use simulated phases to prove
ordering, automatic successful-stage continuation, duplicate prevention and stop
conditions; they do not run the asset assignment. Resume/reference/guard/controller
tests and project Pyright pass. All asset stages remain NOT_STARTED; no continuous
full-asset or forced-context-exhaustion benchmark was performed during setup.

Start after fully restarting OpenCode: **`/bowling-run`**.
