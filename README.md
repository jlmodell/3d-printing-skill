# 3d-printing

A Claude skill for the whole 3D printing loop on Bambu Lab printers: edit and
design STL/3MF files, prepare and run prints, troubleshoot what went wrong, and
keep a print log that makes the second attempt at anything cheap.

Configured out of the box for a **Bambu Lab H2C with a 0.4 mm nozzle and Bambu
PETG Basic**. One clearly marked block in `SKILL.md` is all you edit to point it
at your own machine.

## The problem it solves

Most 3D printing assistance falls down in the same three places:

**Scaling destroys hardware fits.** Ask for "150% of this clock face" and you
get a model whose magnet pockets are now 9 mm instead of 6 mm and whose movement
shaft hole no longer fits any movement you own. This skill scales the *body*
while holding the *interfaces* — magnet holes, bearing seats, screw bosses,
clock movements — at their original physical size, and verifies the result
numerically rather than by looking at a render.

**Fabricated slicer profiles.** A machine profile carries bed shape, toolhead
clearance, purge routines and start/end G-code. Hand-writing one produces a file
that slices without complaint and can drive the toolhead into a printed part
hours in, and you cannot tell good G-code from bad by looking at it. This skill
refuses to invent a profile. It slices with a real one through the Bambu printer
MCP, or hands back a project 3MF built on *your* settings, and never a third
thing that looks like both.

**Troubleshooting starts from zero every time.** The fifth time PETG lifts off
the bed should take thirty seconds, but only if the first four were written
down. The bundled print log records model, material, settings, outcome and — the
field that matters — the fix that actually worked, then queries it before
recommending anything.

## Install

### Claude Code

```bash
git clone https://github.com/TrillyD13/3d-printing-skill ~/.claude/skills/3d-printing
pip install trimesh numpy scipy networkx lxml manifold3d shapely rtree
```

Claude Code picks the skill up automatically on next start.

### Claude Desktop / claude.ai

Package it as a `.skill` archive and upload it in Settings → Capabilities →
Skills:

```bash
git clone https://github.com/TrillyD13/3d-printing-skill
cd 3d-printing-skill && mkdir -p build/3d-printing
cp -r SKILL.md references scripts server build/3d-printing/
cd build && zip -r ../3d-printing.skill 3d-printing
```

## Configure

Open `SKILL.md` and edit the block headed **"Your setup — EDIT THIS SECTION"**.
It is the only installation-specific part of the skill:

```yaml
printer:     Bambu Lab H2C     # drives build volume and fit checks
bambu_model: h2c               # p1s|p1p|p2s|x1c|x1e|a1|a1mini|h2d|h2s|h2c
nozzle:      0.4               # mm
material:    Bambu PETG Basic
slicer:      bambustudio       # bambustudio | orcaslicer
output:      3mf
```

The prose under that block explains each one and what changes if you change it.
If you print with different hardware — a different magnet ecosystem, a different
bearing series — swap the hardware line too; the protected-interface machinery
works the same for any of them.

## Workflow

Every job runs the same shape: **measure → plan → confirm → edit → verify →
deliver.**

1. `scripts/preflight.py` reports which capabilities are actually live and the
   fallback for each that isn't — before anything is promised to you.
2. `scripts/mesh_info.py` and `scripts/detect_features.py` measure the input.
   The mesh is the ground truth: a designer's measured clearance beats any
   catalog dimension.
3. The edit runs through the bundled scripts or short trimesh/build123d code.
4. The output is re-measured. Protected holes within ±0.02 mm, watertight, fits
   the build volume, paint intact if it should be.
5. Print prep goes to the printer MCP if it's live, otherwise to a project 3MF
   built on your own slicer settings.

Renders are a sanity check, never evidence — matplotlib z-sorts imperfectly, so
anything suspicious gets confirmed with a cross-section and a watertightness
check instead.

## Requires

- Python 3.10+
- `trimesh numpy scipy networkx lxml manifold3d shapely rtree`
  (`manifold3d` powers booleans; `rtree` is needed for cavity detection and its
  absence surfaces as a confusing `ModuleNotFoundError` deep inside trimesh)
- **Optional:** a Bambu printer MCP server for slicing, printing and live AMS
  inventory. Without it the skill produces project 3MFs instead — everything
  else works unchanged.
- **Optional:** `build123d` and the bundled render server, for parametric design
  with a visual feedback loop. The server executes the modeling code you send
  it — it binds to loopback only, and [SECURITY.md](SECURITY.md) explains why
  that matters and how to keep it that way. You can delete `server/` entirely;
  nothing else depends on it.

If PyPI is unreachable entirely, `scripts/stl_fallback.py` is numpy + stdlib
only and still covers inspection, protected scaling and STL→3MF.

## What's in it

| File | Purpose |
| --- | --- |
| `SKILL.md` | The skill. Routing, workflows, and the setup block you edit. |
| `scripts/preflight.py` | Capability check. Run first, every time. |
| `scripts/mesh_info.py` | Dimensions, watertightness, object count, colors, units. |
| `scripts/detect_features.py` | Finds holes, pockets and bosses that mate with hardware. |
| `scripts/smart_scale.py` | Scales a body while holding protected interfaces fixed. |
| `scripts/project_3mf.py` | Adds geometry to your own project 3MF without losing paint or settings. |
| `scripts/bambu_3mf.py` | Color assignment and paint-preserving transforms. |
| `scripts/gridfinity_gen.py` | Spec-exact, self-verifying gridfinity baseplates and bins. |
| `scripts/stl_fallback.py` | Dependency-free fallback for the core operations. |
| `scripts/printlog.py` | The print log: record, query, report. |
| `references/` | Deep reference the skill loads on demand — 3MF format, hardware specs, gridfinity constants, print prep, plate arrangement, MakerWorld, printer control, troubleshooting, build123d. |
| `server/` | Optional FastAPI render server for visual CAD iteration. |

## Security

The optional render server in `server/` runs the build123d code you POST to it,
with no sandbox — that's what makes the visual iteration loop work. Both launch
paths bind it to `127.0.0.1` only, including the Docker one, and
[SECURITY.md](SECURITY.md) covers the details, the one line in
`docker-compose.yml` you shouldn't change, and how to reach it from another
machine safely if you need to.

Nothing else in this skill opens a port. The scripts run locally against your
own files, and printer credentials are expected to come from your environment
rather than from any file here.

## Related

For multi-part mechanical assemblies — hinges, snap-fits, sliders, anything with
a moving degree of freedom — this skill deliberately hands off to
[cad-khana](https://github.com/cyberchitta/cad-khana) (Apache-2.0), which
expresses interference and clearance as assertions re-derived from geometry on
every run. Renders tell you a part looks right; assertions tell you it fits.
Two printability constants in `SKILL.md` (the minimum-wall and maximum-overhang
thresholds, with their material-specific adjustments) are adapted from
cad-khana's documented defaults.

## License

MIT — see [LICENSE](LICENSE).
