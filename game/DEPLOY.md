# Bowling 3D → AidenGames LAN deploy runbook

End-to-end path from a change in this Godot project to the live LAN arcade at
`http://192.168.4.70:8091/play/bowling-3d/`.

## Prerequisites

- **Godot 4.7.2** with **Web export templates** installed at
  `~/Library/Application Support/Godot/export_templates/4.7.2.stable/`
  (download `Godot_v4.7.2-stable_export_templates.tpz` from the Godot releases
  and unzip its `templates/*` into that folder).
- **Node 24+** and the AidenGames web `node_modules` (`npm ci --prefix src/AidenGames.Web`).
- **SSH** to the Z6 host as `kingpomf@z6-llm` (strict host key). The deployer
  only manages `aiden-games.service`; it never touches other services.
- The two repos checked out side by side:
  `.../Blender-Bowling-FlashNext` (this game) and `.../AidenGames`.

## 1. Export the web build (this repo)

```sh
godot --headless --path game --export-release "Web" build/web/index.html
node patch_web_export.mjs build/web
```

`patch_web_export.mjs` bypasses Godot's secure-context startup gate (the LAN
site is plain HTTP). Audio is disabled via `audio/driver="Dummy"` in
`project.godot` because `AudioWorklet` is also secure-context-gated. Both are
required or the game will not boot over HTTP.

## 2. (Optional) refresh the screenshot

```sh
CAPTURE_OUT="$PWD/docs/gameplay.png" godot --path game res://scenes/Capture.tscn
```

## 3. Sync into AidenGames

From the AidenGames repo root:

```sh
node scripts/sync-bowling-3d.mjs
```

This copies `build/web` into `src/AidenGames.Web/public/play/bowling-3d/`,
regenerates `release.json` (file hashes), and copies `docs/gameplay.png` to
`public/media/bowling-3d/gameplay.png`. It refuses to run if the export is
missing or unpatched.

## 4. Build, commit, deploy (AidenGames)

```sh
npm run build:z6 --prefix src/AidenGames.Web   # AOT build + hash/manifest builder
git add -A && git commit -m "feat(bowling-3d): <change>"
npm run build:z6 --prefix src/AidenGames.Web   # rebuild so the artifact matches the clean commit
python3 scripts/deploy-z6.py
```

The deployer refuses a dirty tree, uploads an immutable timestamped release,
verifies every hash, validates the Caddyfile, atomically switches `current`,
restarts only `aiden-games.service`, and health-checks the existing games. The
prior release is kept as `previous` for rollback.

## 5. Verify live

```sh
curl -s -o /dev/null -w "%{http_code}\n" http://192.168.4.70:8091/play/bowling-3d/
curl -s -o /dev/null -w "%{http_code} %{content_type}\n" http://192.168.4.70:8091/play/bowling-3d/index.wasm
curl -s http://192.168.4.70:8091/api/games/bowling-3d | head
```

A headless Chromium smoke check (Playwright is in the AidenGames web
`node_modules`) can confirm the engine boots: load the URL, wait ~15s, and
assert the console logs `Godot Engine v...` with no page errors.

## Integration facts (already in place)

- Catalog entry `id 5 / slug bowling-3d` in `content/z6/catalog.json`.
- Dedicated page `src/AidenGames.Web/src/app/bowling-3d-page.ts` + route in
  `app.routes.ts` (before `games/:slug`), with a Play button to `/play/bowling-3d/`.
- Caddy handler `handle /play/bowling-3d/*` in `deploy/z6/Caddyfile` with a CSP
  that includes `'wasm-unsafe-eval'` (required for WebAssembly) and serves the
  `.wasm`/`.pck` as files (not the SPA rewrite).
- `deploy-z6.py` release cap raised from 64MB to 128MB to fit the Godot wasm.

## Rollback

Point the Z6 `current` symlink at the retained `previous` release and restart
only `aiden-games.service` (see `AidenGames/docs/deployment-z6.md`).
