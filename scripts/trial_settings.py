"""Operator-owned identities for the Flash-Next / EliteDesk trial."""
MODEL = 'z6-llama/qwen38-flash-next'
TRIAL = 'bowling52-flash-next-elitedesk-20261025-r1'
CONTEXT = 262144
OUTPUT = 32768
COMPACTION_RESERVE = 49152
WORKER_HOST = 'elitedesk-3060'
WORKER_APP = '/home/kingpomf/blender-new-llm-setup/var/elitedesk52-runtime-65703d9'
WORKER_ROOT = '/home/kingpomf/blender-new-llm-setup/var/mcp-worker'
WORKER_BINARY = '/home/kingpomf/blender-new-llm-setup/tools/blender-5.2.3-linux-x64/blender'
DEDICATED_GPU = True
VISION_HELPER = 'qwen38-27b'  # Fixed image-description API only; never the trial agent.
