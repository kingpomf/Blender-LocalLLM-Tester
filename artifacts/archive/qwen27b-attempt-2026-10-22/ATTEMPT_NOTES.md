# Archived Qwen27B attempt — 2026-10-22

Reset at the user's request after the latest failed attempt. The original ledger and all local attempt directories were preserved before resetting the active workspace.

- Recorded model: `z6-llama/qwen38-27b`.
- Archived ledger status: IN_PROGRESS, next stage 02.
- Ledger claimed Stage 00 PASS for `7399670c3256418f99c46714161d6a0f` and Stage 01 PASS for `742a1f200bac450382529e18594f4e99`.
- The active source recorded in that ledger was `742a1f200bac450382529e18594f4e99`.
- Local downloads contained metadata for 19 jobs; those directories are preserved under `downloads/`.
- No local `.blend` checkpoint, final exports, render PNGs, stage scripts, or validation report were present at reset. Only the model-discovery utility remained in `scripts/`.
- This reset did not independently validate the claimed PASS results or diagnose a specific failure. All claims and job IDs here are historical evidence only.
- No remote jobs were submitted or cancelled; no worker, gateway, model configuration, or asset specifications were changed during reset.

The next run must start at Stage 00 with a new empty isolated scene and no historical `source_job`.
