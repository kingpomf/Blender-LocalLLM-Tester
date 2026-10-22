# Python LSP and Blender 5.2 typing

Updated 2026-10-22 for the project-only Blender 5.2.3 test. This is a tooling
intervention, not a repaired bowling asset or stage PASS. See `RUNTIME_52.md`.

## Configuration

- `opencode.json` enables Pyright with `./.venv/bin/pyright-langserver --stdio`.
- `pyproject.toml` and `uv.lock` pin **Pyright 1.1.414** and
  **fake-bpy-module-5.2 20260730**. The old 4.5 stub package was uninstalled.
- `pyrightconfig.json` uses project Python 3.11, basic checking, and excludes
  historical archives. The worker source is an extra import path for the local
  MCP launcher/operator utilities. Their execution uses the worker's environment.
- Model context and compaction settings are unchanged.

Type stubs do not implement Blender. Execute bpy scripts through the worker,
not local Python. To restore the pinned checker environment:

```sh
uv sync --frozen --python 3.11 --group dev
```

Quit and restart OpenCode to reload the language server and project MCP entry.
Read both checkpoints; preserve the existing source and repair Stage 00.

## Check authoring code before submission

```sh
.venv/bin/pyright artifacts/scripts/stage01.py
opencode debug lsp diagnostics /Users/start/Development/Blender-LocalLLM-Tester/artifacts/scripts/stage01.py
```

The current model-authored stage scripts still contain errors. They were not
rewritten or certified by this installation. Fix confirmed API errors before
resubmitting. `obj.children.link`, `view_layer.objects.link`, unsupported operator
calls, and duplicate keywords must not be waved away as stub false positives.

## Verified checker behavior

- `.venv/bin/pyright testing/blender52/positive.py`: **zero errors**.
- Actual OpenCode LSP diagnostics for that same fixture: **empty diagnostic list**.
- `.venv/bin/pyright testing/blender52/negative.py`: **three expected errors**
  for invalid children.link, bpy.scene and collection_links_add APIs.
- The negative file is intentional and outside normal workspace include paths;
  an explicit check must fail. Diagnostic categories have not been disabled.

## Generated-stub limitations

Dynamic `bpy.context` values and mathutils iteration may still be misinferred.
Use narrow types after verifying the API, e.g.:

```python
from typing import cast
import bpy

scene = cast(bpy.types.Scene, bpy.context.scene)
view_layer = cast(bpy.types.ViewLayer, bpy.context.view_layer)
```

For a vector use explicit coordinates `[obj.location.x, obj.location.y,
obj.location.z]` if the stub lacks iteration typing. These annotations do not
change runtime behavior. Check questionable diagnostics against the actual
5.2 API and runtime evidence, individually; never assume an entire error list
is false positives. LSP success does not prove geometry, dimensions, persistence,
render framing, export portability or acceptance.
