# Qwen3.6 35B A3B MTP UD-Q8_K_XL — installed setup

**Current configuration observation, 2026-10-23:** during the EliteDesk WSL setup,
another configuration change selected native **262,144 tokens**, with no YaRN,
in both the installed Z6 registry and project/global client metadata. This WSL
work preserves that newer setting. The original1.01M qualification below is
historical evidence, not the currently advertised window.

Installed and API-qualified on Z6, 2026-10-23. These are infrastructure checks;
the new BowlingPair01 model trial has not begun.

## Pinned model

- OpenCode ID: `z6-llama/qwen36-35b-a3b-mtp-q8` (main and helper).
- Repository: <https://huggingface.co/unsloth/Qwen3.6-35B-A3B-MTP-GGUF>.
- Revision: `5bc3e238d916f48a861bac2f8a1990a0e9b7e98d`.
- File: `Qwen3.6-35B-A3B-UD-Q8_K_XL.gguf`, **39,099,447,584 bytes**.
- SHA-256: `6c6b816537abad90b250a0972b345466028d861ddfe316d5f0de31ca6440f781`.
- Z6 directory: `/home/kingpomf/models/qwen36-35b-a3b-mtp-q8/`.
- GGUF architecture `qwen35moe`, native context 262,144, one next-token
  prediction layer and embedded MTP tensors verified directly in the header.

The original install completed without changing live configuration or either
service invocation. The operator subsequently ended the coding test and
authorized activation/testing. Existing models and gateway-wide default
`qwen38-27b` remain available. No runtime binary upgrade was required.

## Original maximum-context qualification (historical)

Publisher maximum is **1,010,000** using YaRN extension (native **262,144**).
The original qualified profile used **1,009,920**, the greatest multiple of llama.cpp's 256-token
alignment within that maximum. Input, reasoning, tool history and output share
the same total window. OpenCode output budget is 32,768, not extra context.

- YaRN factor 4, original context 262,144.
- Hybrid CPU/GPU: 12 offloaded layers, layer split 1:1 across both RTX 3060s.
- CPU KV cache (`no-kv-offload`), Q8_0 K/V, flash attention.
- Batch/microbatch 128/32, one slot, predict -1.
- MTP enabled: `spec-type=draft-mtp`, draft maximum 2; native logs confirm a
  real MTP draft context and accepted draft tokens.
- Temperature 1.0, top-p .95, top-k 20, min-p 0, repeat penalty 1.
- Reasoning budget 2,048, embedded Jinja template, 20-minute unprotected idle unload.
- Text-only: the publisher currently excludes `--mmproj` with MTP. The separately
  selected vision-capable Qwen3.8 27B profile inspects reference pixels first and
  writes the construction guide. MTP remains the Blender coding model.

## Verification and tuning evidence

- Pinned file size and full SHA-256 matched.
- Initial 20-layer / microbatch-128 profile failed with CUDA compute-buffer OOM;
  the gateway restored Nemotron. Reduced offload/microbatch solved this.
- An unaligned 1,010,000 context was rounded to 1,010,176 by llama.cpp; the strict
  gateway identity check rejected the mismatch. The aligned profile fixes it.
- Final installed backend reports the expected model/path, one slot and
  **n_ctx=1009920**, with no GPU diagnostic errors.
- Chat, parsed `add_numbers(a=17,b=23)`, tool-result round trip and SSE completion passed.
- Short-generation logs show actual draft acceptance (including 6/8 and 4/6
  tokens in two checks). These are smoke measurements, not MTP speedup benchmarks.
- Post-smoke GPU readings: 9,195 MiB / 11,067 MiB. These are observations, not peaks.
- The full million-token prompt was **not** benchmarked. Configured allocation
  and short-request success do not establish long-context retrieval quality.
- Remote accepted API evidence: model directory `acceptance-attempt3.json`.
  Earlier failed attempts remain in `acceptance.json` and `acceptance-attempt2.json`.
- Installed registry snapshot: gateway `shared/router/20261023T231440994650Z/`.
  Backups are retained; restoring a prior profile requires the normal strict-idle
  migration/rollback procedure, never editing a running INI.
- Fresh OpenCode process completed a real read-tool call and returned the fixture
  marker through the production endpoint. Session `ses_e94ec62d1ffesVZA01Bf38852p`;
  evidence: gateway `var/phase6-validation/opencode-qwen36-35b-a3b-mtp-q8-attempt3.json`.
  An initial short-deadline session was cancelled during prefill; a completed
  second test exposed a relative-path fixture assumption. The final test used
  the explicit absolute fixture path. Those records are preserved separately.

## Fresh Blender trial and image-first workflow

Previous Nemotron ledgers, scripts, native outputs, downloaded artifacts and guard
state are hash-archived at
`artifacts/archive/nemotron-final-before-qwen36-2026-10-23/`.
All five accepted jobs were remotely terminal before reset; no old source or
stage PASS is reused. The fresh guard has no accepted jobs or failures.

The new trial queue is `var/bowling52-qwen36-mtp-q8-20261023`, Blender 5.2.3 LTS,
CPU rendering. Automatic compaction/pruning are enabled, the60-step cap is removed,
and stages run consecutively. All ten Blender stages are NOT_STARTED.

imageMCP uses **EliteDesk WSL Qwen Image 2.1 Q4** for this reference recipe; Z6
Turbo remains a distinct available profile. Run `/bowling-references` first:
the installed Qwen3.8 vision model generates references through imageMCP, downloads
and inspects the actual pixels, then saves receipts and visual observations.
Open a fresh MTP session and run `/bowling-start` afterward. The authoring wrapper
checks real decoded images, job receipts, distinct outputs and visual guide before
reserving any Blender job. Reference planning is not a Blender-stage PASS.

Fully quit and restart OpenCode, then open a fresh session in this checkout.
