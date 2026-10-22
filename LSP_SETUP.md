# Python LSP and Blender typing

Enabled locally on 2026-10-22 at the operator's request. This is a tooling change
to the active 256K attempt, not a new build or a stage PASS.

## Configuration

- `opencode.json` explicitly enables the `pyright` server for `.py` and `.pyi`
  using `./.venv/bin/pyright-langserver --stdio`. The existing LSP tool permission
  remains allowed. In OpenCode 1.18.34, omitting `lsp` leaves language servers off;
  permission to call a tool does not enable the server.
- `pyproject.toml` / `uv.lock` pin **Pyright 1.1.414** and
  **fake-bpy-module-4.5 20260730** in a project-local development environment.
- `pyrightconfig.json` selects the `.venv` imports, Python 3.11 target and basic
  type checking. Current scripts/helpers/tests are included; historical archives,
  `.opencode`, and `.venv` are excluded from workspace scanning.
- Existing 262,144-token model selection and disabled compaction/pruning are
  retained. No remote worker dependencies or model services are changed.

The `fake-bpy-module` package provides **type stubs**, not a working Blender
runtime. Use this environment for checking only. Execute actual `bpy` scripts
through the Blender worker, not local Python.

## Install or restore

From the repository root:

```sh
uv sync --frozen --python 3.11 --group dev
```

Quit and restart OpenCode after configuration changes, then resume the existing
session/checkpoint. Configuration is not hot-reloaded into running sessions. The
active attempt is preserved; no reset or automatic repairs are performed here.

## Check before submitting authoring code

```sh
.venv/bin/pyright artifacts/scripts/stage09.py
```

To inspect the actual OpenCode LSP integration:

```sh
opencode debug lsp diagnostics /absolute/path/to/artifacts/scripts/stage09.py
```

Fix syntax errors and confirmed API/signature errors before resubmission. A
completed diagnostic command with reported errors means the checker is working,
not that the script passed. Do not repeatedly rewrite unrelated string formatting
when the diagnostic identifies a duplicate keyword or unknown exporter option.

## Verified behavior

- Both Pyright CLI and **OpenCode's actual LSP diagnostics command** return
  diagnostics for the existing Stage 09 script, including
  `Parameter "export_texcoords" is already assigned`,
  `Parameter "export_apply" is already assigned`, and unsupported exporter keywords.
- An isolated negative fixture flags invalid `bpy.scene` and a duplicate keyword.
- An isolated positive fixture using Blender 4.5 export arguments and typed
  Scene/ViewLayer references reports zero errors. Fixtures were analyzed only,
  not executed, and do not repair the actual asset.

## Typing limitations

Generated Blender stubs approximate a dynamic API. In this pinned version,
Pyright can misinfer `bpy.context.view_layer` as `MethodType` and incorrectly flag
the valid `.objects.active` access. A narrow type annotation can disambiguate it:

```python
from typing import cast
import bpy

view_layer = cast(bpy.types.ViewLayer, bpy.context.view_layer)
view_layer.objects.active = obj  # obj is an actual Blender Object
```

This is typing assistance, not a runtime check. Verify questionable diagnostics
against the worker version's API rather than inventing replacement properties.
LSP checks do not validate dimensions, rendering angles, source provenance, or
whether every required acceptance check was actually performed. Failed validation
must remain FAIL even when its Python program executed successfully.
