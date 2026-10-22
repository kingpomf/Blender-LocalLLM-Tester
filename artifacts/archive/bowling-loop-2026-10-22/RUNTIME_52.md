# Project-scoped Blender 5.2 trial — 2026-10-22

## Installed and selected

- Official Blender **5.2.3 LTS**, Linux x64, build `e13b728c6880`.
- Binary on Z6: `/home/kingpomf/Development/blender-new-llm-setup/tools/blender-5.2.3-linux-x64/blender`.
- Official archive SHA-256: `78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec`.
- Archive/checksum source: <https://download.blender.org/release/Blender5.2/>.
- Local stubs: **fake-bpy-module-5.2==20260730**, wheel SHA-256
  `bc8faaafabd277b347128a2fb5189f7b635427812a1832e69295c14589965fe8`.
- Pyright remains **1.1.414**; local checker Python remains 3.11. Stubs are not an executable Blender runtime.

`opencode.json` selects `scripts/blender52_mcp.py`, the existing worker's Python
environment, and the separate Z6 queue
`/home/kingpomf/Development/blender-new-llm-setup/var/bowling-blender52`.
The wrapper reuses installed worker code without modifying that repository.
Global OpenCode settings, the old 4.5 binary/queue and gateway configuration were
not changed. Restart OpenCode to load this project entry point and new stubs.

## Rendering scope

Use `blender_render(..., device="CPU")`. The wrapper rejects GPU submissions
before they reach the gateway. The shared GPU renderer is separately pinned to
4.5 and the original source queue; it cannot be used as a 5.2 renderer merely by
changing the CPU binary. All rendered evidence for this trial must use 5.2 CPU.
GPU, AI-video and shape generation are unavailable through this project wrapper.
CPU renders have existing worker resource/time limits; keep review samples low
and submit individual views when necessary.

## Verified installed behavior

Fresh project MCP process and real sandboxed Z6 jobs passed:

| Check | Job / evidence |
| --- | --- |
| 5.2.3 authoring, scene-linked collection, parenting, GLB export | dd05ed88004845078c02193dac32cf19 |
| Native reopen and GLB round trip; mesh, material and parent retained | 78d06de2f63d4273b0eb3178b585accf |
| Cycles CPU render, 320×240 PNG; visibly reviewed blue triangle | 085da980f1f0400ca9d40101c773cb7f |
| GPU request rejected before submission | runtime-evidence.json |
| Original bowling native source reopened on 5.2.3 | 69331f6eb0ee40e88b2a01bde90980c0 |
| Pyright and actual OpenCode LSP positive fixture | zero errors |
| Negative fixture | three expected API errors; checks are not suppressed |
| Resume regression suite | eight tests passed |

Detailed manifests, artifact hashes and accepted IDs are in
`testing/blender52/runtime-evidence.json`. Fixtures are infrastructure tests, not
bowling assets. Initial MCP startup failed before any submission due to an
instruction-property setter; it was fixed and qualification explicitly resumed.

## Existing bowling work and diagnosis

The source `d5c68e4d5c834c378c60a77882ab00be` was copied from `var/mcp-worker`
into the test queue with its original completed row, manifest and scene hash
`b15ff084653abb28bae4f44f3a55efda83ec04df2b9d0512cf0c3f4923a6ce04`.
This was a file/metadata migration, not a repeated submission or a 5.2 build PASS.
Original failed jobs stay in the original queue. The local native checkpoint and
`artifacts/scripts/stage00.py` / `stage01.py` are unchanged by this migration.

Native reopen shows only `BowlingPair01_ROOT` and `Scene Collection`. Stage 00
created collections with `bpy.data.collections.new()` but never linked them into
`scene.collection.children`. Its pre-save inventory was insufficient acceptance
evidence. Stage 00 is now FAIL, not PASS. Repair it before advancing.

The transcript also contains real API errors and geometry defects, not just stub
limitations: `root.children.link` is invalid parenting; use `obj.parent = root`.
`view_layer.objects.link` is invalid; link objects into a scene-linked collection.
The proposed lane helper never scales its Y extent to the required length and
offsets it twice. Arrow vertices coincide; flattened cones produce degenerate dot
geometry. These require model repairs and measured checks after the upgrade.
Some dynamic context/vector diagnostics can still be stub limitations. The
positive fixture demonstrates narrow `cast` annotations and explicit coordinates;
do not dismiss all errors or disable attribute checking.

## Continue or roll back

Restart OpenCode, open a new session and use `/bowling-start`. Resume the copied
repair base in the 5.2 queue, repair/revalidate Stage 00, and record the runtime
intervention. Do not present this as an uninterrupted 4.5 trial.

To roll back configuration, restore the original MCP command
`uv --directory /Users/start/Development/blender-new-llm-setup run --frozen --extra mcp python -m blender_worker.mcp_server`
and remove the four project `BLENDER_SSH_TARGET`, `BLENDER_REMOTE_APP`,
`BLENDER_REMOTE_ROOT`, `BLENDER_REMOTE_BINARY` overrides so machine defaults apply.
Restore `fake-bpy-module-4.5==20260730`, run `uv lock` and
`uv sync --frozen --python 3.11 --group dev`, then restart OpenCode.
Reconcile the original queue/checkpoints before using its sources. Never send
new 5.2-native files to 4.5 as an assumed compatible rollback. Keep both runtimes
and queues for evidence; no cleanup or deletion is required.
