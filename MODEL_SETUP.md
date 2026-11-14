# Selected trial — Qwen3.8 Flash-Next / Strata

User selected **z6-llama/qwen38-flash-next**, installed backend **Strata**,
IQ3_S Flash-Next. The installed profile is enabled at a verified262144 context.
OpenCode output cap32768, reasoning enabled/interleaved reasoning_content.
Automatic compaction/pruning,49152 reserve; tool outputs160 lines/12000 bytes.
This uses the existing qualified model/engine; no runtime/sampling changes here.

Clean linked worktree: /Users/start/Development/Blender-Kart-Simplified,
branch project/kart-simplified. Prior Turbo kart trial is scrapped/archived and
bowling remains paused in its separate checkout. No old source/checkpoint or
generated geometry is inherited. BUILD -> REVIEW -> DELIVER remains the protocol,
with RUN_STATE.json as the sole asset ledger and unchanged supplied assistance.

The worker uses existing Blender5.2.3 LTS in the isolated queue
kart-simplified-flash-next-strata-20261025-r1. Downloads stay under this worktree.
Bounded polling sleeps1/2/5/10/15 and fixed consistency/delivery checks are allowed;
GPU coding protection is preserved and the normal gateway handles admission.
There is no manual GPU ownership change or lease release in this launch.

Launch: python3 scripts/run_kart.py --detach
Status: python3 scripts/run_kart.py --status
The ignored process/session journal is not a second progress ledger. Client exit0
alone is not asset acceptance. Existing interactive OpenCode sessions need restart
to load the model/config; the launcher creates a new process and session.
