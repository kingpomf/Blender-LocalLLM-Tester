# Flash-Next / Strata bowling profile

Primary model z6-llama/qwen38-flash-next through the existing Z6 Strata gateway.
Configured context262144/output32768, interleaved reasoning_content support,
compaction/pruning with49152 reserve and bounded tool output. Neither weights,
sampling, native context, protected leases nor gateway ownership are changed.

Blender runs on EliteDesk, not the Z6 GPUs: installed/qualified5.2.3 LTS, CPU
scene authoring/validation, CUDA rendering on the existing shared dedicated queue.
Active worker code is the immutable elitedesk52-runtime-65703d9 snapshot; queue
root stays /home/kingpomf/blender-new-llm-setup/var/mcp-worker so all EliteDesk GPU
operations remain serialized. The trial's own guard/progress IDs are isolated
locally. Old jobs from other clients are never chosen as starting asset sources.

Fresh OpenCode processes load the selected profile. Existing interactive OpenCode
processes must restart for the upgraded global EliteDesk worker configuration.
