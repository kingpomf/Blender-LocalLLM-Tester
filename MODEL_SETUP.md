# Nemotron 3.5 Bolt E4B — 64K setup

Replaces the retired Blender-specialist model on Z6, 2026-10-23. Runtime
integration checks are not a Blender asset capability result.

## Model and pinned weights

- OpenCode ID: `z6-llama/nemotron35-bolt-e4b`.
- Display name: **Nemotron 3.5 Bolt E4B Q8 (64K)**.
- Repository: <https://huggingface.co/unsloth/NVIDIA-Nemotron-3.5-Bolt-E4B-GGUF>.
- Revision: `2104306495395ad940bc1365381a09c59a1a1600`.
- File: `NVIDIA-Nemotron-3.5-Bolt-E4B-UD-Q8_K_XL.gguf`.
- Size: **8,192,955,584 bytes**.
- SHA-256: `6176bd788769bd58042c165d3dc8e8c86a8ca5c90d5de188a364b31dc9560810`.
- Z6 path: `/home/kingpomf/models/nemotron35-bolt-e4b/NVIDIA-Nemotron-3.5-Bolt-E4B-UD-Q8_K_XL.gguf`.
- Architecture: Gemma-4-E4B; publisher describes approximately 8B total / 4B effective parameters.
- Text-only profile; no vision projector or DFlash drafter installed.

Both the project main and helper models select this ID. The global OpenCode
model list replaces the retired entry with this one. Other installed models and
the gateway-wide default `qwen38-27b` are preserved.

## Context and inference settings

**65,536 tokens total runtime context**, shared by input, reasoning, tool history
and generated output. OpenCode advertises context 65,536 and output budget 16,384;
these are not independent 64K input plus 64K output allowances.

The publisher/Unsloth guide recommends 64K for E4B. The GGUF metadata declares
131,072, but this installation deliberately uses the documented 64K guidance,
without context extension. Project automatic compaction/pruning remain disabled;
work one stage per invocation and checkpoint before context exhaustion.

Existing llama.cpp build **b11604 / 45451c366** supports this model. No binary
upgrade was needed. Native router, full layer offload, split 1:1 across both RTX
3060s, flash attention, Q8_0 K/V caches, batch/microbatch 256/128, one slot,
20-minute unprotected idle unload, speculation disabled, Jinja enabled.

Sampling: temperature 1.0, top-p .95, top-k disabled, min-p 0, repeat penalty 1.
Thinking enabled, reasoning budget 2,048 tokens, conversational mode disabled.
The model's embedded chat template is used without a custom replacement.

## Installed verification

- Pinned download size and SHA-256 matched.
- Existing gateway was idle in a pre-existing RECOVERY_REQUIRED state. Explicit
  reconciliation restored normal ownership before strict-idle registry migration.
  No active requests or protected leases were interrupted/released.
- Gateway discovery removes the old model and advertises the new one at 65,536.
- Actual loaded backend reports alias `nemotron35-bolt-e4b`, `n_ctx=65536`.
- Chat, parsed function call arguments, tool-result round trip and SSE completion
  passed. SSE test reconstructs content across chunks, rather than requiring a
  response string to appear within one chunk.
- A **55,038-token input**, plus 7 output tokens, completed with the expected
  marker. This is a capacity check, not a retrieval-quality benchmark.
- Post-request GPU usage: GPU 0 **3,217 MiB**, GPU 1 **3,335 MiB**; no GPU
  diagnostics errors. These are observed readings, not guaranteed peak usage.
- Detailed remote evidence: gateway `shared/nemotron-bolt-20261023.acceptance.json`.
- A fresh real OpenCode process used the new model through the production
  endpoint, completed one read-tool call and returned the fixture marker.
  Session: `ses_e95935b7bffettgmnHxZ4Lki9E`.
- Registry migration: `shared/router/20261023T201450349819Z/` in the Z6 gateway.

## Retirement and evaluation state

The retired `qwen38-blender-35b` GGUF was hash-checked before deletion:
**16,478,599,264 bytes removed**, no remaining matching HF repo cache. Its active
router, source registry template, global client and project client entries were
removed. Historical audit documents/immutable rollback backups remain evidence;
they do not represent available weights and must not be blindly rolled back.
Old installation notes are under `artifacts/archive/retired-model-2026-10-23/`.

The final old-model scripts, scenes, claimed passes and stopped guard were
preserved at `artifacts/archive/blender52-specialist-final-2026-10-23/` during the
separately authorized reset. A fresh Nemotron trial now uses queue
`var/bowling52-nemotron-20261023`, all ten stages NOT_STARTED and an empty guard.
No asset implementation or old PASS is reused. Model installation/qualification
does not count as asset-stage work. Later resets still require explicit approval.

Fully quit and restart OpenCode, then open a fresh session to load the new global
and project model entries. Blender stays 5.2.3; the CPU-only authoring/render
workflow and separately prepared EliteDesk GPU renderer are unchanged.
