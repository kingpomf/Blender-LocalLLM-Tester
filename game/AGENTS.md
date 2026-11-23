# Bowling 3D — working notes

Godot 4 single-lane bowling demo built from the accepted **BowlingPair01** asset.
It also ships to the **AidenGames** LAN arcade as "Bowling 3D". This folder
(`game/`) is the game's source of truth; the Blender asset trial that produced
the GLBs is a separate, archived workflow — do not re-run it from here.

## Layout

- `project.godot` — Godot 4.3+ project. `audio/driver="Dummy"` is intentional
  (see Deploy); it also silences the native build, which has no audio anyway.
- `scenes/` — `Main.tscn` (controller), `Pin.tscn`, `Ball.tscn`, `Capture.tscn`
  (dev screenshot). `scripts/` — `game.gd`, `ball.gd`, `pin.gd`, `scoring.gd`,
  `capture.gd`. `tests/test_scoring.gd` — headless scoring checks.
- `assets/models/` — GLBs copied from `../artifacts/exports/`.
- `export_presets.cfg` — single-threaded Web preset. `patch_web_export.mjs` —
  post-export HTTP/LAN patch. `docs/gameplay.png` — catalog screenshot.

## Run / test

```sh
godot --path game                                   # play (Godot 4.7+)
godot --headless --path game --import               # import assets
godot --headless --path game -s tests/test_scoring.gd   # scoring unit checks
```

Controls: Left/Right aim, hold/release Space to charge and bowl, R restart frame,
N new game. Make one focused change per revision and re-run the scoring checks.

## Deploy to AidenGames (LAN)

Full runbook in [DEPLOY.md](DEPLOY.md). Short version: export → `node
patch_web_export.mjs build/web` → from the AidenGames repo `node
scripts/sync-bowling-3d.mjs` → `npm run build:z6 --prefix src/AidenGames.Web` →
commit → `python3 scripts/deploy-z6.py`.

## Commit / push

- This repo (`Blender-LocalLLM-Tester`): game work is on branch
  `feature/bowling-game`; push to `origin`.
- AidenGames: integration is on branch `feature/bowling-3d`; push to `origin`.
- Do not commit the tool-owned `HANDOFF.md` status flips or the `.godot/` cache.

## Caveats (internal HTTP LAN)

- Godot Web needs a secure context; the LAN site is plain HTTP, so the export is
  patched (`patch_web_export.mjs`) and uses the Dummy audio driver. Re-apply both
  after any re-export. The game runs **silent**.
- The deployer release cap was raised to 128MB to fit the Godot wasm.
- Gutters are visual only (side bumpers); no spin/hook yet; right lane is scenery.
