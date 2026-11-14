# EliteDesk Blender5.2.3 runtime

Installed binary /home/kingpomf/blender-new-llm-setup/tools/blender-5.2.3-linux-x64/blender,
portable libraries under tools/sandbox-runtime/usr/lib/x86_64-linux-gnu. Direct
host version probes need that library path; isolated worker commands mount it
automatically. This is an existing qualified runtime, not a new download.

Worker code snapshot: var/elitedesk52-runtime-65703d9. The existing shared CPU/GPU
queue root var/mcp-worker is retained so GPU work remains serialized. Idle CPU/GPU
runners were replaced only after admission transactions proved both queues empty,
no live warm GPU session existed and no GPU compute process was present. Queue
histories/databases were backed up; no Z6 service/lease was touched.

The fresh bowling guard tracks only this trial's accepted IDs. Its authoritative
asset source is always a completed EliteDesk CPU job; render IDs may be gpu-
prefixed. Version/lineage/hash checks remain enforced. Never import a Z6 source ID.

A separate real CPU-author/CUDA-render fixture passed: CPU job5be7ced08d644157af0ebc8eabbf14f1,
GPU jobgpu-d3aa492287204d10bdd52b47676395dd, actual RTX3060 CUDA/cpu_enabled=false,
Blender5.2.3 LTS,512x512/8 samples, wall2.90s. This is infrastructure qualification,
not a comparative full-asset performance benchmark or bowling acceptance evidence.
