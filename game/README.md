# Bowling Game (Godot 4)

A single-lane bowling demo built from the accepted **BowlingPair01** asset. The
left lane's pins are read from the imported GLB at runtime and replaced with
dynamic physics pins; you bowl at them with an aim + charge control. Standard
ten-pin scoring (strikes, spares, tenth-frame bonus balls) is implemented in
`scripts/scoring.gd`.

## Requirements

- **Godot 4.3+** (standard build, GDScript). The project uses no C#.

Install on macOS with Homebrew if needed:

```sh
brew install --cask godot
```

## Run

Open this folder (`game/`) as a project in the Godot editor and press **F5**, or
from a terminal:

```sh
godot --path game
```

On first launch Godot imports the GLB models into `.godot/` (ignored).

## Controls

| Action        | Key(s)                       |
|---------------|------------------------------|
| Aim left/right| `Left` / `Right` arrows      |
| Charge power  | Hold `Space`, release to bowl|
| Restart frame | `R`                          |
| New game      | `N`                          |

Power ping-pongs 0–100% while `Space` is held; release to lock it. The cyan bar
in front of the ball shows the launch line.

## Project layout

```
game/
  project.godot
  icon.svg
  assets/models/   BowlingPair01.glb, BowlingPin01.glb, BowlingBall01.glb,
                   BowlingPair01_Collision.glb  (copied from artifacts/exports)
  scenes/          Main.tscn, Pin.tscn, Ball.tscn
  scripts/         game.gd, ball.gd, pin.gd, scoring.gd
```

## How it works

- `game.gd` instances `BowlingPair01.glb`, finds `Pin_L_01..10`, records their
  global transforms (the glTF Y-up conversion is applied by the importer), hides
  the static originals, and spawns `Pin.tscn` rigid bodies at those transforms.
- A `StaticBody3D` lane collider (floor + side bumpers) is built from the pin
  layout so the ball rolls and stays in play.
- `Ball.tscn` is a `RigidBody3D` with a `0.108 m` sphere collider; it is held
  frozen at the approach until launched.
- A pin counts as knocked down when it tilts past ~60° or slides off its spot.

## Known limitations (first playable)

- Gutters are visual only; side bumpers keep the ball in play (bumper bowling).
- No hook/spin control yet; aim is a straight lateral angle.
- Right lane is present as scenery only.
- Pin collision uses capsule/cylinder approximations per the asset guide.

## Working on this game

- [AGENTS.md](AGENTS.md) — instruction set for editing, running and testing.
- [DEPLOY.md](DEPLOY.md) — full runbook to ship to the AidenGames LAN arcade
  (export → patch → sync → build → commit → deploy → verify → rollback).

The game is deployed to AidenGames as **Bowling 3D**
(`http://192.168.4.70:8091/play/bowling-3d/`). Because that LAN profile is plain
HTTP and Godot Web needs a secure context, the export is patched
(`patch_web_export.mjs`) and uses `audio/driver="Dummy"`; re-apply both after any
re-export. See DEPLOY.md.
