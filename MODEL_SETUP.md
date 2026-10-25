# Selected model — Qwen3.8 Turbo fresh trial

- OpenCode model ID: **z6-llama/qwen38-turbo**.
- Installed gateway advertises it enabled; model state was unloaded at discovery.
- Configured context139264, output16384; tool calls and reasoning enabled.
- Both reference planner (build) and asset coder (bowling-coder) use this model.
  The coding agent has no shell/delegation tools and uses enforced MCP workflows.
- Compaction/pruning enabled,32768 reserve, no configured step cap; tool outputs
  capped at160 lines/12000 bytes. The native139264 context remains accurately set.
- Confirmed context-only failures use bounded checkpoint reconciliation and a
  fresh coding context; they are not treated as native Blender failures.
- Fixed pixel-description helper remains qwen38-27b and is separately attributed;
  concepts are generated using qwen-image-2.1-q4 on EliteDesk WSL.

`scripts/trial_settings.py` owns model/queue identities; opencode.json and all four
bowling command profiles must agree. `scripts/preflight_blender52.py` verifies the
fresh effective OpenCode config and live MCP tool/runtime catalog. Use
`scripts/probe_coding_model.py z6-llama/qwen38-turbo` for read-only model discovery.
Discovery does not prove inference success; verify the detached session's actual
model/tool activity separately. Existing interactive OpenCode processes require
a quit/restart to load these model/config changes.

The previous Qwen3.6 trial was archived in full. No old session, source file or
asset acceptance is active. Do not copy archived meshes into the clean trial.
