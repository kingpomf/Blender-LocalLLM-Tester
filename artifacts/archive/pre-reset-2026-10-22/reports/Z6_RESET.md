# Z6 reset — 2026-10-21

## Post-upgrade review: repaired and cleared

The subsequent review found three reproducible gaps: welded-analysis topology
reporting can falsely claim watertightness, unpacked textures disappear across
job revisions, and an exception immediately after deployment drain can leave
admission closed. All three findings are now repaired and installed from worker
commit `82a62e0`. The installed runtime and gateway are healthy, and the review
hold in `BUILD_STATUS.md` is cleared.
Full evidence: `blender-new-llm-setup/docs/AUTHORING_REVIEW_2026-10-21.md` in the
sibling worker repository. No Kart01 build or model evaluation was run.

Repair checks: Mac 71 passed / 15 Linux skips; Z6 lifecycle/schema/deployment
fault injection 17 passed; staged and installed real MCP authoring checks passed.
The disconnected fixture now reports 12 vertices / not watertight and rejects
STL export. Packed texture pixels survive a source revision and CPU/CUDA render.
Missing/unsupported dependencies fail explicitly. Admission recovery and later
file/config rollback passed mock fault injection. Existing MCP workflow passed
22 calls with zero unexpected errors. Installed evidence in the worker checkout:
`var/authoring-acceptance/1792634680938980000/acceptance.json`.
CUDA job: `gpu-8e5affa9271d4476905dd8302e72f197`. Runtime hashes/source seal verify;
gateway is healthy, ready and not draining. Model services were preserved.

## Result

Project reset and configuration verified. The initial interface and recovery blockers are now resolved by the authorized worker upgrade. The fresh Kart01 evaluation is **READY at Stage 00**, with all stages PENDING. Worker fixture jobs were run for API acceptance; no Kart01 build or model inference was submitted.

## Preserved previous work

- The pre-existing uncommitted Stage 00 PASS is preserved in `artifacts/archive/pre-z6-2026-10-21/BUILD_STATUS.md`, including the original stale run metadata.
- The prior `artifacts/blend/Kart01.blend` was moved without overwrite to `artifacts/archive/pre-z6-2026-10-21/Kart01.blend`.
- Archived Blender file SHA-256: `2ce9ff792e75dadbcf03b45d1ef2921d507f6c2d4bdc4bc722c89f9c661f75a0`.
- No previous build PASS carries into the fresh ledger. No specification files were changed.

## Selected setup

- Model and small model: `z6-llama/qwen38-27b` (Qwen3.8 27B Dense).
- Experimental alternative discovered: `z6-llama/qwen38-turbo`.
- Provider endpoint, authentication, and model capabilities inherit from the existing global OpenCode provider. No credentials were copied into this repository.
- Blender endpoint: existing global `z6-blender-worker`, explicitly enabled here.
- All six other inherited MCP servers are disabled for this project.
- Replaced the obsolete project Ollama override and removed the old project auto-resume plugin declaration. The kickoff stops at a failed or unsupported stage.
- Updated `AGENTS.md`, `/kart-start`, README, and the active ledger for the selected host and compatibility gate.

## Verification actually run

| Check | Evidence |
| --- | --- |
| Installed OpenCode | `1.18.34` |
| Authenticated read-only Z6 `/v1/models` | Advertised `qwen38-27b` and `qwen38-turbo`; selected model present |
| `opencode debug config` | Parsed successfully; model/small model Dense; only `z6-llama` enabled; provider inherited; only Z6 worker enabled |
| `opencode mcp list` | `z6-blender-worker connected`; other six servers disabled |
| Live Z6 worker capabilities | Authoring available; repaired runtime seal verified; gateway healthy, `CODING_PROTECTED` / ready. Initial recovery state is resolved. |
| Archived scene | File present; SHA-256 recorded above |
| `git diff --check` | Passed |
| `git diff -- spec/kart-01` | Empty; challenge requirements unchanged |

Model discovery can be repeated manually with `python3 artifacts/scripts/check_z6_models.py`. It uses existing global credentials without printing them and submits no inference. It is an operator setup check, not part of the evaluated model's permitted workflow.

The advertised model list proves discovery, not successful generation. MCP connectivity and capabilities prove availability of that interface, not successful Kart01 execution or current GPU rendering.

## Initial blockers and resolution

1. **Modeling interface — resolved:** installed `blender_scene_author(code, source_job?)` on Z6. It provides general Blender Python inside the existing CPU sandbox, immutable source revisions, reports and native saves. Acceptance covered empty collections/units, custom geometry, parents, node materials, camera/light, PNG/GLB, native reopen, unchanged inspection, isolation and failed assertions. Installed evidence is in the worker repository's `var/authoring-acceptance/1792633325821370000/acceptance.json`; a real queued CUDA render of the custom scene passed as `gpu-4c4d1acaf2c24f23b02b414f85e8ab84`. No Kart01 stage is marked passed by these fixtures.
2. **GPU ownership — resolved:** with explicit user authorization, inspected ownership/GPU/queue/lease state. Recovery reason was a changed backend process/boot identity. There were no active requests, protected leases, or nonterminal jobs; coding router health was `ok`, both coding models were unloaded, and GPU utilization was zero. `POST /recovery/reconcile {"acknowledge":true}` succeeded without service operations or lease release. The later authoring upgrade used a guarded gateway restart and refreshed worker source pins, preserving model-service identities. After the CUDA fixture, gateway health is `ok`, ownership `CODING_PROTECTED`, handoff `ready`.

## Current launch and delivery path

Quit and restart OpenCode in this repository, then run `/kart-start`. It checks `authoring.available=true` and begins a fresh isolated Stage 00. Author scripts are retained under `artifacts/scripts/`; remote job/source IDs are recorded before polling. Verified artifacts download into this checkout's `artifacts/downloads/JOB_ID/`; narrow repository-local copy/hash commands place checkpoints and deliveries at the unchanged spec paths. The archived previous run is retained.

Resolved project configuration was checked with `opencode debug config`: Dense selected, only Z6 MCP enabled, download override applied, and remote worker settings inherited. `opencode mcp list` connects. Specifications remain unchanged. The user authorized publication of the verified worker repair and tester reset/configuration.

A fresh MCP session using that resolved project configuration exposed `blender_scene_author` and fetched the fixture's hash-verified `report.json` into `artifacts/downloads/a1357fc9d4fc4f3aa9ab533d2da05b71/`. This confirms the actual project artifact path, rather than just the JSON declaration; the fixture is not a Kart01 checkpoint.
