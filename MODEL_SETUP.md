# Blender specialist model — 65K setup

Installed and verified on Z6 on 2026-10-22. This is model setup evidence, not a Kart01 stage PASS.

## Selected model

- OpenCode ID: `z6-llama/qwen38-blender-35b`.
- Display name: **Qwen3.8 35B A3B Blender v1 (65K)**.
- Repository: <https://huggingface.co/JohnDOeNNN/Qwen3.8-35B-A3B-APEX-Abliterated-Blender-v1-GGUF>.
- Revision: `4c9be4c2e1660d6dde2ca34e63539d3f4d8f59bf`.
- File: `a3b-apex-abl-blender-v1-merged.gguf`, 16,478,599,264 bytes.
- Verified SHA-256: `379571667085706be63119716ad59dec8e66c7c180b8cd4d592546a2c95ba279`.
- The publisher's merged GGUF is used directly; no separate LoRA or re-quantization.
- Server and OpenCode context: **65,536 tokens**. OpenCode output budget: **16,384 tokens**, sharing the total context window.
- Text input/output, reasoning and tool calls. No vision projector is configured for this model.

The existing `z6-llama` provider's authentication and endpoint are inherited. Both project `model` and `small_model` select this model to avoid title/helper requests switching to a different coding model. Global defaults and existing model entries are preserved.

## Runtime profile

The existing protected gateway/native llama.cpp router serves this model across both RTX 3060s: full layer offload, layer split 1:1, flash attention, Q8_0 K/V caches, batch/microbatch 256/128, one slot, Jinja template enabled, speculation disabled, reasoning budget 2048, and 20-minute unprotected idle unloading. Context uses the publisher's documented 65,536-token setting without a context-extension override.

Sampling defaults: temperature .6, top-p .95, top-k 20, min-p 0, repetition penalty 1. These are setup defaults, not a publisher benchmark reproduction.

The model card targets Blender **5.2**, while this project's worker was verified as **4.5.14 LTS**. The agent must use the actual version reported by worker capabilities/job artifacts and consult matching APIs. The Blender worker was not upgraded for this installation.

## Verification

- Download size and pinned Hugging Face SHA-256 matched.
- Registry migration used the existing strict idle drain and rollback helper; no protected leases were released.
- Live gateway discovery advertises the model with `context_window=65536`.
- Loaded backend reports `model_alias=qwen38-blender-35b`, **`n_ctx=65536`**, and no GPU diagnostic errors.
- Short chat, parsed tool-call arguments and tool-result round trip, and SSE completion passed.
- GPU memory immediately after the short chat: GPU 0 used 8647 MiB/free 3256 MiB; GPU 1 used 8299 MiB/free 3613 MiB.
- A fresh OpenCode process read `WORKER_GUIDE.md` with the actual read tool and replied `BLENDER_OPENCODE_READY`. Session: `ses_e9c70e932ffeVPGEpoYfhfe8IR`.
- Source registry validation and its 11 targeted unit tests passed. OpenCode configuration loading and model listing passed.

These checks verify the configured window and basic inference/tool integration. They do not measure saturated 65K prompt performance or validate the model's generated Blender code. No Kart01 build was started; all 10 stages remain NOT_STARTED.

## Start the test

1. Quit and restart OpenCode in this repository.
2. Open a new session; confirm the selected model is **Qwen3.8 35B A3B Blender v1 (65K)**.
3. Run `/kart-start`.

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
- Z6 synthetic API evidence: `shared/qwen38-blender-35b-20261022.acceptance.json` in the gateway deployment.
- Mac OpenCode evidence: `z6-gpu-gateway/var/phase6-validation/opencode-qwen38-blender-35b.json` and its corresponding events file.

To return this project to the previous default, select `z6-llama/qwen38-27b` for `model` and `small_model` and restart OpenCode. Existing models remain installed. Router rollback, if needed, uses the gateway's documented `migrate_router.py --rollback` helper with the exact backup above at an idle boundary; no rollback was performed during this installation.
