# Changelog

## Unreleased: multi-material interlock

- `references/multimaterial_interlock.md`: why soft + rigid parts peel. It
  covers separate objects and boundary avoidance on thin parts (sliced
  here: no beams on a 1.6 mm strip at the default), plus per-pair beam,
  temperature and speed settings, when to use which lock, and sources.
- `scripts/mm_interlock.py`: build123d mushroom pegs, dovetail seams and
  rivets with defaults for 0.4 and 0.2 nozzles. `apply_lock`, `verify_pair`,
  and a one-object multi-part 3MF export with filament slots, plus STLs.
- `scripts/interlock_coupon.py`: a five-coupon test plate (butt, dovetail,
  pegs, flat, rivet).
- SKILL.md: multi-material bonding is on by default, and bonded pieces are
  one object with parts.

## 1.0.0

First public release.

Consolidates four previously separate skills into one, because the paths shared
too much context to stay split:

- **Mesh editing and print prep** — inspection, feature detection, protected
  scaling, paint-preserving 3MF transforms, project-3MF output.
- **Slicing and printing** — MakerWorld sourcing, plate arrangement and
  stacking, printer control and AMS through a Bambu printer MCP.
- **Parametric design** — build123d with an optional local render server for a
  visual feedback loop.
- **Print log** — record and query print history; troubleshooting reference.

Also in this release:

- All installation-specific values collected into one editable block in
  `SKILL.md`, so the skill can be pointed at a different printer without
  reading through the rest of it.
- Slicing routed through a real machine profile via the printer MCP, with the
  project-3MF path kept as the fallback when no MCP is connected. The skill
  will not fabricate a machine profile under any circumstances.
- Multi-part mechanical assemblies handed off to
  [cad-khana](https://github.com/cyberchitta/cad-khana) rather than attempted
  with renders alone.
