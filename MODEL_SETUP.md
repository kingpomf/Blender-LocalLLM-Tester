# Blender specialist model — native 256K setup

Installed and verified on Z6 on 2026-10-22, then raised from 65,536 to 102,400 and now **262,144 tokens**. This is model setup evidence, not a Kart01 stage PASS. The 256K update does not reset or repair the active attempt; see `SESSION_REVIEW_2026-10-22.md` before resuming it.

## Selected model

- OpenCode ID: `z6-llama/qwen38-blender-35b`.
- Display name: **Qwen3.8 35B A3B Blender v1 (256K)**.
- Repository: <https://huggingface.co/JohnDOeNNN/Qwen3.8-35B-A3B-APEX-Abliterated-Blender-v1-GGUF>.
- Revision: `4c9be4c2e1660d6dde2ca34e63539d3f4d8f59bf`.
- File: `a3b-apex-abl-blender-v1-merged.gguf`, 16,478,599,264 bytes.
- Verified SHA-256: `379571667085706be63119716ad59dec8e66c7c180b8cd4d592546a2c95ba279`.
- The publisher's merged GGUF is used directly; no separate LoRA or re-quantization.
- Server and OpenCode context: **262,144 tokens**. OpenCode output budget: **16,384 tokens**, sharing the total context window. The existing 8,000-token compaction reserve remains configured; compaction can still occur below the total window limit.
- Text input/output, reasoning and tool calls. No vision projector is configured for this model.

The existing `z6-llama` provider's authentication and endpoint are inherited. Both project `model` and `small_model` select this model to avoid title/helper requests switching to a different coding model. Global defaults and existing model entries are preserved. The project publishes a matching 262,144-token model metadata override.

## Runtime profile

The existing protected gateway/native llama.cpp router serves this model across both RTX 3060s: full layer offload, layer split 1:1, flash attention, Q8_0 K/V caches, batch/microbatch 256/128, one slot, Jinja template enabled, speculation disabled, reasoning budget 2048, and 20-minute unprotected idle unloading. The original setup used the publisher's example 65,536-token setting; the current 262,144-token setting matches the installed GGUF's declared native maximum and needs no context-extension override.

Sampling defaults: temperature .6, top-p .95, top-k 20, min-p 0, repetition penalty 1. These are setup defaults, not a publisher benchmark reproduction.

The model card targets Blender **5.2**, while this project's worker was verified as **4.5.14 LTS**. The agent must use the actual version reported by worker capabilities/job artifacts and consult matching APIs. The Blender worker was not upgraded for this installation.

## Verification

### Original 65K installation

- Download size and pinned Hugging Face SHA-256 matched.
- Registry migration used the existing strict idle drain and rollback helper; no protected leases were released.
- Live gateway discovery advertises the model with `context_window=65536`.
- Loaded backend reports `model_alias=qwen38-blender-35b`, **`n_ctx=65536`**, and no GPU diagnostic errors.
- Short chat, parsed tool-call arguments and tool-result round trip, and SSE completion passed.
- GPU memory immediately after the short chat: GPU 0 used 8647 MiB/free 3256 MiB; GPU 1 used 8299 MiB/free 3613 MiB.
- A fresh OpenCode process read `WORKER_GUIDE.md` with the actual read tool and replied `BLENDER_OPENCODE_READY`. Session: `ses_e9c70e932ffeVPGEpoYfhfe8IR`.
- Source registry validation and its 11 targeted unit tests passed. OpenCode configuration loading and model listing passed.

Those original checks verified window allocation and short-request integration, not a saturated-window benchmark or generated Blender correctness.

### Historical 100K configuration

- The strict idle migration changed only this live model's context to **102,400**; other models, weights, split/cache/batch settings, and gateway default are preserved.
- Gateway discovery advertises 102,400 and actual backend props report `n_ctx=102400`.
- Chat, tool-call/tool-result round trip, and SSE completion passed.
- A synthetic **70,039-token input**, exceeding the old window, returned `LONG_CONTEXT_OK` with 4 output tokens in **44.13 seconds**. This is a capacity test, not long-document retrieval quality.
- After that request, GPU 0 used 8975 MiB/free 2928 MiB; GPU 1 used 8627 MiB/free 3285 MiB, with no diagnostic errors.
- A fresh OpenCode process passed a real read-tool smoke at the 102,400-token setting, session `ses_e9c24f0cfffe9iHhNIs0dF52Zb`.
- All build stages were reset afterward; no qualification request counts as a Kart01 stage PASS.

### Current 256K configuration

- Gateway discovery and actual loaded backend props both report **262,144 tokens**. Other model entries/options and the selected weights are unchanged.
- Chat, parsed tool-call/tool-result round trip, and SSE completion passed.
- A synthetic **160,039-token input**, larger than the old 102,400 window, returned `LONG_CONTEXT_OK` with 4 output tokens in **134.45 seconds**.
- Post-request memory: GPU 0 used 10271 MiB/free 1632 MiB; GPU 1 used 9923 MiB/free 1989 MiB. Gateway health is ok with no diagnostic errors.
- A fresh OpenCode process passed the real read-tool smoke with 262,144-token metadata, session `ses_e9be350a6ffer1oH7vguyzGdZi`.
- This proves native-window allocation and capacity above the old limit, not saturated 256K throughput, long-document retrieval quality, or reliable Blender validation.
- No current build artifacts, ledger PASS claims, or source scenes were repaired or reset by the context upgrade.

## Start the test

1. Quit and restart OpenCode in this repository.
2. Open a new session; confirm the selected model is **Qwen3.8 35B A3B Blender v1 (256K)**.
3. Review `SESSION_REVIEW_2026-10-22.md` and reconcile the current inconsistent ledger/handoff before resuming with `/kart-start`. A context increase is not a new asset build or an acceptance result.

The existing worker guide remains important: unconditional stage calls, explicit `source_job` chaining, and actual scene/report verification still apply.

## Diagnostics update and recovery qualification

The Z6 worker now exposes `blender_job_diagnostics` for bounded traceback retrieval
from failed CPU jobs. Restart OpenCode before the next test. Fresh scenes contain
zero objects; use `bpy.context.scene.unit_settings.system` for units. Never delete
a default Cube by unconditionally indexing its name, or loop over artifact fetches
after a job has failed.

The actual model's strict baseline one-repair fixture **failed**: it recovered
eventually but exceeded the repair budget and had an invalid source-ID argument.
A separately labelled fixture with explicit source/units API guidance **passed**
in 7 tool calls, with exactly one diagnostics call and one repaired job. This is
integration/recovery evidence, not a promise of autonomous kart-build success.
Full records: worker repository `docs/DIAGNOSTICS_2026-10-22.md`.

## Operator provenance

- Z6 weights: `/home/kingpomf/models/qwen38-blender-35b/a3b-apex-abl-blender-v1-merged.gguf`.
- Installed registry/preset and pre-change rollback backup: `/home/kingpomf/Development/z6-gpu-gateway/shared/router/20261022T121952974911Z/`.
- Historical 100K registry/preset and pre-change rollback backup: `/home/kingpomf/Development/z6-gpu-gateway/shared/router/20261022T133557716621Z/`.
- Current 256K registry/preset and pre-change rollback backup: `/home/kingpomf/Development/z6-gpu-gateway/shared/router/20261022T144449199807Z/`.
- Z6 synthetic API evidence: `shared/qwen38-blender-35b-20261022.acceptance.json` in the gateway deployment.
- Z6 100K API/capacity evidence: `shared/qwen38-blender-35b-100k-20261022.acceptance.json`.
- Z6 256K API/capacity evidence: `shared/qwen38-blender-35b-256k-20261022.acceptance.json`.
- Mac 256K client evidence: `z6-gpu-gateway/var/phase6-validation/opencode-qwen38-blender-35b-256k.json`.
- Mac OpenCode evidence: `z6-gpu-gateway/var/phase6-validation/opencode-qwen38-blender-35b.json` and its corresponding events file.

To return this project to the previous default, select `z6-llama/qwen38-27b` for `model` and `small_model` and restart OpenCode. Existing models remain installed. To revert only the latest context increase, use the gateway's `migrate_router.py --rollback` helper with the **256K pre-change backup** above at an idle boundary and restore client context metadata to 102,400. No rollback was performed for the 256K update.
