# 3d-printing

A Claude skill for the whole 3D printing loop: edit and design STL/3MF files,
prepare prints, troubleshoot what went wrong, and keep a print log that makes
the second attempt cheap.

This fork is set up for Jeff's printers: **Bambu A1, A1 mini, and X1 Carbon**
(Bambu 3MF), a **Snapmaker U1** with four toolheads (Orca-style 3MF, filament
slots), and an **Anycubic Kobra X** (STL, including a 0.25 mm hotend). Default
material is **PETG at 245/70 on smooth PEI**. A Bambu printer tool is not
required. The setup block in `SKILL.md` is the install. His notes are
`references/jeff_*.md`.

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
refuses to invent a profile. It hands back the file that printer uses — a Bambu
3MF, a U1 Orca-style 3MF, or a Kobra STL — and does not require a Bambu printer
tool to do it.

**Troubleshooting starts from zero every time.** The fifth time PETG lifts off
the bed should take thirty seconds, but only if the first four were written
down. Jeff's print log is `print-log.md` in the designs repo. Read it before
recommending a setting, and append the fix that actually worked.

## Install

### Claude Code

```bash
git clone https://github.com/jlmodell/3d-printing-skill ~/.claude/skills/3d-printing
pip install trimesh numpy scipy networkx lxml manifold3d shapely rtree
```

Claude Code picks the skill up automatically on next start.

### Claude Desktop / claude.ai

Package it as a `.skill` archive and upload it in Settings → Capabilities →
Skills:

```bash
git clone https://github.com/jlmodell/3d-printing-skill
cd 3d-printing-skill && mkdir -p build/3d-printing
cp -r SKILL.md references scripts server seed build/3d-printing/
cd build && zip -r ../3d-printing.skill 3d-printing
```

## Configure

Jeff's block is already filled in under **"Your setup — EDIT THIS SECTION"** in
`SKILL.md`. Output depends on the printer. Fits, charm specs, and the
seigaiha rules are in `references/jeff_fits.md`, `references/jeff_charms.md`,
and `references/jeff_design_rules.md`.

Designs and the print log belong in
[grokalok-jmo-3d-designs](https://github.com/jlmodell/grokalok-jmo-3d-designs):
`designs/<project>/vN/` with a mesh, a short README, `NOTES.md`, and `images/`.
That repo was not reachable from here, so the same tree is seeded at
`seed/designs-repo/` (18-entry `print-log.md`, templates, Git LFS rules for
images and STL/3MF). Google Drive "3D Prints" is the backup copy. Old
revisions stay until he OKs a print and confirms the list.

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
5. Print prep hands back a Bambu 3MF, a U1 Orca-style 3MF, or a Kobra STL.
   A Bambu printer tool is optional, and only for the three Bambu machines.

Renders are a sanity check, never evidence — matplotlib z-sorts imperfectly, so
anything suspicious gets confirmed with a cross-section and a watertightness
check instead.

## Worked example

A 80 × 60 × 10 mm plate with four features: two D6×3 magnet pockets, a D30×6
clock-movement pocket, and a D8 decorative through-hole. Scale it to 150%.

```bash
python scripts/detect_features.py part.stl        # measure before deciding anything
python scripts/smart_scale.py part.stl scaled.stl --scale 1.5 \
  --protect "cyl:-30,-20,1.5,0,0,1,6.000,3.000,blind" \
  --protect "cyl:30,-20,1.5,0,0,1,6.000,3.000,blind"
```

Measured on the output:

| | before | after 1.5× | |
| --- | --- | --- | --- |
| Body | 80 × 60 × 10 | 120 × 90 × 15 | scaled |
| Magnet pockets (protected) | D6.0 × 3.0 blind | **D6.0 × 3.0 blind** | held |
| Movement pocket | D30 × 6 blind | D45 × 9 blind | scaled |
| Decorative hole | D8 through | D12 through | scaled |

The magnets still press-fit. Everything you didn't protect grew with the body.
That distinction is the whole point — a uniform 1.5× would have left you with
9 mm pockets and no magnet that fits them.

## Requires

- Python 3.10+
- `trimesh numpy scipy networkx lxml manifold3d shapely rtree`
  (`manifold3d` powers booleans; `rtree` is needed for cavity detection and its
  absence surfaces as a confusing `ModuleNotFoundError` deep inside trimesh)
- **Optional, and not required:** a Bambu printer tool for the A1, A1 mini, or
  X1 Carbon. The U1 and the Kobra X are not Bambu machines. Without that tool
  the skill still delivers the file for the target printer.
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
| `scripts/mm_interlock.py` | build123d mechanical locks (pegs, dovetails, rivets) for bonded multi-material parts; one-object multi-part 3MF export. |
| `scripts/interlock_coupon.py` | Printable soft/rigid interlock test plate. Rules in `references/multimaterial_interlock.md`. |
| `scripts/stl_fallback.py` | Dependency-free fallback for the core operations. |
| `scripts/printlog.py` | Optional local JSON log. Jeff's history is the designs-repo `print-log.md`. |
| `references/` | Deep reference loaded on demand, including `jeff_*.md` (printers, materials, fits, design rules, charms, projects, workflow). |
| `seed/designs-repo/` | Seed for the designs repo: print log, `NOTES.md` template, project README template, Git LFS attributes. |
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
