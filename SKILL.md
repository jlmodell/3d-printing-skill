---
name: 3d-printing
description: >-
  Complete 3D pipeline for Bambu Lab printers; the only skill for 3D work. Use for any .stl
  or .3mf file, or to scale, resize, recolor, change filament colors, mirror, rotate, split,
  merge, repair, measure, or add/resize magnet holes - even if the format isn't named. Also
  designing printable parts (bins, organizers, brackets, mounts, gridfinity), build123d CAD,
  MakerWorld - browse models, find me a model - print prep and printing - slice, print, fit
  on one plate, multi-object plate, batch print night, check printer, what's printing, AMS -
  troubleshooting - stringing, warping, bed or layer adhesion, support removal, clogs,
  elephant foot, ringing, under-extrusion, this keeps happening - and the print log: log this
  print, what settings did I use, what worked for this filament, did I fix this before,
  filament usage. When scaling, holds hardware interfaces (Maker's Supply
  parts, MH011 movement, bearings, inserts) and magnet holes at original size while the body
  scales. Jeff's printers: Bambu A1, A1 mini, X1 Carbon, Snapmaker U1, Anycubic
  Kobra X. Default PETG 245/70 on smooth PEI. Also charms, seigaiha, U1, Kobra,
  and TPU.
---

# 3D Printing

Edit, design, prepare and print 3D files the way a careful machinist would:
measure first, confirm intent, protect functional interfaces, verify after.

This skill is one entry point for the whole loop: editing and designing files,
preparing and running prints, and keeping the print log that makes the second
attempt at anything cheap. Deliberately one skill rather than four — the paths
share too much context to split. The one thing it hands off is **cad-khana**,
for multi-part mechanical assemblies; see Designing new parts.

**For mesh work the local Python stack is the primary path.** Printing does not
require Bambu's printer tool. Hand Jeff the file his target printer actually
uses (Your setup, below). A Bambu tool is optional, and only for the A1, A1
mini, or X1 Carbon, and only when it is already live. The Snapmaker U1 and the
Anycubic Kobra X are not Bambu machines. Other externals (OrcaSlicer CLI,
OpenSCAD MCP, render server) are useful when present and frequently absent, and
the failure is silent until you are deep into a job. Preflight decides the
local paths. See `references/external_tools.md` and `references/jeff_printers.md`.

## Step 0 — preflight, every run, before promising anything

```bash
python scripts/preflight.py
```

It reports which capabilities are live and prints the fallback for each that is
not. Run it before you tell the user what you are going to do, not after you
have failed to do it. It costs a second and it is the difference between
"here's your file" and "actually, I can't."

Non-negotiables it enforces:

- **Never fabricate a machine profile to make a slicer run.** If no profile for
  the user's printer exists, output a project 3MF instead (below).
- **Never route design work to the OpenSCAD MCP** unless `ListConnectors`
  shows it live. preflight checks for a local `openscad` binary, not the
  connector — MCP liveness is a `ListConnectors` question. Default to
  build123d and the bundled scripts.
- **Never guess `bambu_model`.** Only the A1 (`a1`), A1 mini (`a1mini`), and
  X1 Carbon (`x1c`) have one, and only if a Bambu tool is actually live. The
  U1 and the Kobra X do not. A wrong model drives a wrong machine profile.
- A missing capability is information, not a blocker. Every one has a fallback.
  A missing Bambu tool is not a blocker. Deliver the file anyway.

preflight cannot see MCP connectors. Do not wait on a Bambu connector before
choosing the output file. Output follows the printer in Your setup.

## Your setup — EDIT THIS SECTION

**This block is Jeff's install.** Apply it without re-asking, and re-read it if
a job seems to contradict one. The long form is `references/jeff_*.md`.
Routing, saving a design, and the print log below follow this block.

This install is Jeff's. He does not own an H2C. Do not require Bambu's printer
tool. Where a later section still says H2C, or tells you to slice through a
Bambu connector before you can deliver, follow this block and
`references/jeff_printers.md` instead.

```yaml
printers:
  - name: Bambu Lab A1            # 256×256 mm, AMS lite. Height was not recorded.
    bambu_model: a1               # only if a Bambu tool is already live
    output: bambu-3mf
  - name: Bambu Lab A1 mini       # 180×180 mm. Check fit before using it.
    bambu_model: a1mini
    output: bambu-3mf
  - name: Bambu Lab X1 Carbon     # 256×256 mm, AMS
    bambu_model: x1c
    output: bambu-3mf
  - name: Snapmaker U1            # 4 toolheads, "271 plate". Multi-material, including TPU.
    slicer: snapmaker-orca
    output: orca-3mf              # filament slots assigned
    slots:                        # Karambit memory
      1: {name: navy, hex: "#1B2A4A"}
      2: {name: cream, hex: "#F3EEE0"}
  - name: Anycubic Kobra X        # 260×260×260 mm. Slots: dark blue, gold, brown, white. No cream.
    hotend_mm: [0.4, 0.25]
    slicer: anycubic-slicer-next
    output: stl
nozzle: 0.4                       # mm, hardened steel on every printer. Kobra X also has a 0.25 hotend.
material: PETG
nozzle_temp: 245
bed_temp: 70
bed: smooth PEI
layer_height: 0.2
designs: https://github.com/jlmodell/grokalok-jmo-3d-designs
print_log: print-log.md           # in the designs repo. Read it, then append.
drive_backup: Google Drive "3D Prints"
```

- **Printers: the five above.** Pick the one that fits the part and the
  materials. The U1 is the multi-material machine (four toolheads). The A1
  mini is 180 mm and is too small for a lot of his parts. Bed and file format
  per machine: `references/jeff_printers.md`. There is no single `bambu_model`.
- **Material: PETG at 245 °C / 70 °C bed.** That is the default, including for
  the U1. An older A1 template used 255/80. Do not switch to it unless he
  asks. Secondary materials and the bonding pairs that failed are in
  `references/jeff_materials.md`. Shrinkage stays in the slicer. Do not
  pre-scale the mesh. ABS dryer parts use about 100.5% XY compensation as a
  slicer setting (Spool), not a mesh scale.
- **Bed: smooth PEI.** For TPU, smooth PEI has bonded hard enough to tear.
  Use textured PEI or glue for TPU-first parts. Plate history is in
  `references/jeff_materials.md`.
- **Nozzle: 0.4 mm hardened**, on every printer. Offer that first. The Kobra X
  also has a 0.25 mm hotend. A 0.25 job **FAILED** to send until the
  touchscreen nozzle and the Anycubic 0.25 preset matched. See
  `references/jeff_printers.md`.
- **Output, per printer. Do not require a Bambu tool.**
  - A1, A1 mini, X1 Carbon: a Bambu 3MF.
  - U1: an Orca-style 3MF with filament slots. Default slot 1 navy `#1B2A4A`,
    slot 2 cream `#F3EEE0`. Not a Bambu Studio project renamed to look like one.
  - Kobra X: STL. The cloud slicer wants STL. Heavy 3MF imports freeze
    Anycubic Slicer Next.
  - In every multi-part 3MF, each piece is a separate named object.
- **Charms.** Default to the studio spec: 2.4 mm stitch holes, a 0.6 mm
  groove, art sunk 0.8 mm into pockets, slicer interlocking for 2–3 layers,
  TPU body and PLA art. The Charm bot's tested spec (1.7 mm holes, 1.2×0.6 mm
  groove, art sunk 0.6 mm, face-up) is the proven alternative. Do not mix
  them. `references/jeff_charms.md`.
- **Fits, seigaiha, chamfers, hardware.** `references/jeff_fits.md`,
  `references/jeff_design_rules.md`, `references/jeff_projects.md`. Great Wave
  seigaiha is the motif he wants on almost everything. Design around the
  hardware he owns (`references/jeff_workflow.md`).
- **Designs and the print log** live in the designs repo above. Read
  `print-log.md` before advising. Append it after a result. Save each design
  as `designs/<project>/vN/` with the mesh, a short README, `NOTES.md`, and
  `images/` (a preview at save time, and his print photos when he sends
  them). Drive "3D Prints" is a backup copy. Delete old revisions only after
  he OKs a print and confirms the exact list. If that repo cannot be cloned,
  use `seed/designs-repo/` here and say so. `references/jeff_workflow.md`.
- **Talking to him.** Show a preview image before you build. Keep messages
  short. Do not invent slicer setting names or print results. Keep
  **FAILED** and **UNTESTED** labels.

These four are not printer-specific — keep them whatever your setup:

- **When modifying a file the user uploaded, edit that file — do not deliver a
  differently-named copy.** Same filename, their project intact.
- **Never silently rescale magnet holes.** Report the measured size, identify
  the likely magnet, ask whether to keep (default) or change.
- Generated artifacts go to a working/temp directory, never `~/Downloads`
  unless the user asks for a one-off there.
- Never write printer serials, LAN IPs, access codes or account tokens into any
  file in this skill. See Privacy.

## Environment setup (once per session)

```bash
pip install trimesh numpy scipy networkx lxml manifold3d shapely rtree --break-system-packages
```

`manifold3d` powers booleans; `rtree` is required for `section().polygons_full`
(cavity detection) and its absence shows up as a confusing `ModuleNotFoundError`
deep inside trimesh. If PyPI is blocked entirely, `scripts/stl_fallback.py` is
numpy + stdlib only and covers inspection, protected scaling and STL→3MF.

## Routing

```text
User wants something 3D
├── Has an STL/3MF to change?         → Core workflow, then Color changes /
│                                      Other common edits (below)
├── Scaling a model with hardware?    → Protected scaling — the signature move
├── Wants a new part designed?        → Designing new parts
│   ├── Multi-part assembly that
│   │   must fit together?            → hand off to cad-khana
│   ├── Single parametric part        → build123d (+ render server if up)
│   ├── Gridfinity                    → scripts/gridfinity_gen.py
│   └── Organic / sculpted            → MakerWorld instead
├── Wants to find an existing model?  → references/makerworld.md
├── Which printer, or what file?      → Your setup, then references/jeff_printers.md
├── Material, plate, TPU, bonding?    → references/jeff_materials.md
├── Fit, clearance, detent, flex?     → references/jeff_fits.md
├── Seigaiha, chamfer, construction?  → references/jeff_design_rules.md
├── Charm?                            → references/jeff_charms.md
├── A named project of his?           → references/jeff_projects.md
├── Where to save, or what he owns?   → references/jeff_workflow.md
├── Ready to print?                   → Print preparation and output
│   ├── Bambu A1 / A1 mini / X1C      → Bambu 3MF. A live Bambu tool may slice;
│   │                                    it is not required (jeff_printers.md)
│   ├── Snapmaker U1                  → Orca-style 3MF, filament slots assigned
│   ├── Anycubic Kobra X              → STL
│   ├── More than one part?           → separate named objects;
│   │                                    references/plate_arrangement.md for the plate
│   └── Multi-plate 3MF handed in?    → identical-plate check, then stack if
│                                      eligible (plate_arrangement.md)
├── "Print night" / batch session?    → references/plate_arrangement.md
├── Print finished, or went badly?    → Print log and troubleshooting
└── Settings question / recurring     → designs-repo print-log.md FIRST, then
    problem?                            references/troubleshooting.md,
                                        then references/jeff_*.md
```

## Core workflow

Every job: **measure → plan → confirm → edit → verify → deliver.**

1. **Inspect.** `scripts/mesh_info.py <file>` on every input. Note dimensions,
   watertightness, object count, colors, units. STL has no units — assume mm but
   sanity-check.
2. **Detect functional features** whenever an edit could move or resize
   geometry: `scripts/detect_features.py <file>`. The original model was
   designed around real hardware, so **the mesh is the ground truth** — trust
   measured sizes over catalog guesses.
3. **Confirm the plan** with AskUserQuestion when there is a real decision:
   which holes are hardware vs. cosmetic, keep-or-change magnet size, how to
   handle leftover space, what bin mix. Skip only for trivial unambiguous edits.
   For Jeff, show a preview image before building. A mechanism needs a corner
   or a cross-section. See `references/jeff_workflow.md`.
4. **Edit** with the bundled scripts or short custom trimesh/build123d code.
5. **Verify numerically.** Re-run mesh_info and detect_features on the output.
   Protected holes within ±0.02 mm, watertight, fits the build volume, paint
   intact if it should be.
6. **Deliver** the file for the target printer (Bambu 3MF, U1 Orca-style 3MF,
   or Kobra STL) with a short summary of measured before/after numbers. Save
   the design as in "Saving a design" below.

**Renders are a sanity check, not evidence.** Matplotlib and the bundled render
server both z-sort imperfectly; a base that looks detached in a render is
usually a depth-sort artifact. Confirm with cross-sections and
`is_watertight`/`body_count` before believing a render or acting on one.

## Scaling with protected interfaces (the signature move)

"Scale this up 150%" on a model with a clock-movement pocket and magnet holes
means: scale the *body*, keep the *interfaces*.

```bash
python scripts/smart_scale.py input.stl output.3mf --scale 1.5 \
  --protect "cyl:cx,cy,cz,ax,ay,az,diameter,depth,through|blind" [...]
```

- Run detect_features.py first; propose the protected set. Holes matching known
  hardware/magnets are protected by default; decorative holes scale.
- `--mode recut` (default, needs manifold3d): plugs, scales, re-cuts at original
  diameter and depth. Robust at any scale factor. Changes topology → destroys
  paint; warn first.
- `--mode project`: scales then projects hole walls back to original radius and
  compresses blind pockets to original depth. Preserves topology and therefore
  paint. Best for modest factors and plain cylinders.
- Blind-hole depth is preserved in both modes — a magnet doesn't get thicker
  when the model grows. Through-holes stay through.
- Bosses that fit *into* hardware use `boss:` instead of `cyl:`.
- Sanity-check before committing: ≥1.5 mm wall around each preserved hole for
  PETG; no preserved holes now overlapping or breaching a face. If violated,
  tell the user instead of producing a broken model.

## Designing new parts

Three local paths, in preference order. OpenSCAD only if `ListConnectors` shows
the MCP live — otherwise it is not an option, not a fallback; its workflow is in
`references/external_tools.md`.

**0. Multi-part mechanical assemblies — hand off to `cad-khana`.** Anything
where parts must fit *each other* — hinges, snap-fits, sliders, clevis/pin
joints, boxes with lids, anything with a moving DOF — is that skill's job, not
this one's. It declares interference and clearance as assertions and re-checks
them from geometry on every run, which is a stronger guarantee than looking at a
render and deciding it seems fine. Route to it early; retrofitting assertions
onto a finished model wastes the pass. Come back here for print prep, plate
arrangement and printing.

**1. Parametric solids — build123d.** For single parts, and for geometry with no
fit relationship to assert. Headless build123d is the workhorse. When
the bundled render server is up you also get eyes: POST code, look at the PNG,
iterate. Read `references/build123d.md` for the cheatsheet, the server API and
the setup commands. preflight reports whether the server is running and where
build123d lives — it is often inside `server/.venv` rather than system python.
The server is optional; cross-sections verify geometry better than renders do.

**2. Gridfinity — `scripts/gridfinity_gen.py`**, spec-exact and self-verifying:

```bash
python scripts/gridfinity_gen.py fit --size 228.28x150.43        # cells that fit
python scripts/gridfinity_gen.py baseplate --size 228.28x150.43 --out bp.stl
python scripts/gridfinity_gen.py bin --cells 2x3 --units 15 --out bin.stl
```

Read `references/gridfinity.md` before changing any constant. Every generated
part is re-measured at the four profile heights and must read
35.60 / 37.20 / 37.20 / 41.50 mm.

**3. Existing model — MakerWorld.** Best for organic or sculpted shapes, and for
anything a community has already solved well. See `references/makerworld.md`.

Design constants for all paths: wall ≥1.2 mm (3 perimeters at 0.4 mm),
`$fn`/tessellation high enough that curves read smooth, and match the original
designer's measured clearance when remixing rather than applying a nominal one.
For a new part of his, the clearances in `references/jeff_fits.md` replace a
generic 0.2 mm friction fit. The 0.2 mm figure is only a starting point when
those notes are silent.

Two thresholds worth stating in numbers rather than vibes, borrowed from
cad-khana's printability defaults:

- **Wall thickness.** The two numbers above and here are the same rule measured
  two ways: 1.2 mm is 3 × a 0.4 mm *nozzle*, 1.5 mm is 3 × a typical 0.4 mm
  *extrusion width*. Use **1.2 mm as the hard floor** and **1.5 mm as the
  working default** — below it, walls slice as one or two perimeters with no
  infill room and under-extrude into a single ribbon. On a 0.6 mm nozzle the
  default is ≈2.0 mm. Rigid load-bearing parts go **above** 1.5 mm, not at it.
- **Maximum overhang 45°** is the rule for PLA with good part cooling. Adjust by
  material and cooling, in both directions: ABS, or PETG printed **without a
  part fan**, wants 35–40°; ASA, well-cooled PLA, or a slicer with aggressive
  overhang modifiers can reach 50–55°. His own prints have used ≤45°, and
  45° wedges in place of flat overhangs (`references/jeff_design_rules.md`).
  Tighten that if a part shows droop. Do not loosen it just to make a part
  pass. Design for the angle or plan supports.

**Bounded iteration.** Cap the repair loop at 3–5 attempts on the same failure,
feeding each failure into the next attempt rather than restarting. Past that,
stop and say what is stuck and why — two requirements trading off against each
other, a constraint that may be infeasible. A clean "stuck here because X" beats
a long thrash, and most people would rather be told than handed something that
almost works.

## Saving a design

Do this whenever you save a design, not only when he asks. The repo is
`https://github.com/jlmodell/grokalok-jmo-3d-designs`. Layout and templates are
also in `seed/designs-repo/` if that repo cannot be cloned.

1. Create `designs/<project>/vN/`. Leave older versions in place. If he
   uploaded a file to edit, still change that file in place. This folder is
   the kept revision, not a renamed substitute.
2. Put the mesh in that folder. Bambu 3MF, Orca-style 3MF, or STL, matching
   the printer. Git LFS tracks images, STL, and 3MF (`.gitattributes`).
3. Write a short `README.md`: printer, material, settings, status
   (`templates/version-README.md`).
4. Write `NOTES.md` from `templates/NOTES.md`: what changed, printer, material,
   slicer settings, fit results, what worked or failed, next steps. Keep
   **PROVEN**, **FAILED**, and **UNTESTED** honest.
5. Save a preview image in `images/` and embed it in `NOTES.md`. Add slicer
   screenshots the same way. When he sends a photo of the real print, add it
   under `images/` and embed it.
6. Update `designs/<project>/README.md` so it links this version and shows a
   thumbnail (`templates/project-README.md`).
7. Copy the same files to Google Drive "3D Prints" as a backup.
8. Delete an old revision only after he OKs a print and confirms the exact
   list.

## Print preparation and output

Deliver a file. Do not require Bambu's printer tool, and do not wait on it.
`references/plate_arrangement.md` still applies when there is more than one
part: each piece is a separate named object.

- **Bambu A1, A1 mini, or X1 Carbon** → a Bambu 3MF. `scripts/bambu_3mf.py`
  and `scripts/project_3mf.py` are for those machines. If a Bambu tool happens
  to be live, `references/printer_control.md` can slice. Pass `bambu_model`
  `a1`, `a1mini`, or `x1c` from Your setup. Never guess, and never refuse the
  file because the tool is absent.
- **Snapmaker U1** → an Orca-style 3MF with filament slots assigned. Default
  slot 1 navy `#1B2A4A`, slot 2 cream `#F3EEE0`. Do not pass this off as a
  Bambu project. Do not invent a machine profile.
- **Anycubic Kobra X** → STL. See `references/jeff_printers.md` for the 0.25 mm
  nozzle mismatch and the slicer-freeze workaround.
- **No real profile for the machine you are slicing** → do not slice, and do
  not invent one. `references/print_prep.md` is the Bambu "add it to his own
  project 3MF" fallback. It is not the U1 or Kobra path, and it is not a
  requirement that a Bambu connector be live.

```bash
python scripts/project_3mf.py add-part  --project p.3mf --object 8 \
    --mesh part.stl --print-scale --name "..." --out p.3mf
python scripts/project_3mf.py add-plate --project p.3mf \
    --mesh a.stl b.stl --extruder 6 --name "Bins" --out p.3mf
python scripts/project_3mf.py inspect --project p.3mf
```

- `add-part` fuses a body into an existing object as a second part — the
  original triangle list and its paint are untouched, and the slicer fuses
  parts anyway, so the print is identical to a boolean union without the loss.
- `add-plate` computes the plate-grid offset from the project's own bed size and
  shelf-packs the parts. Verify afterwards that everything is on-bed.
- Choose the plate pattern by the geometry, using the clearance values in the
  project's `project_settings.config` — not folklore. See
  `references/plate_arrangement.md`.
- Never read a profile's display color as the user's loaded filament. Call
  `get_printer_filaments` when the MCP is live; otherwise inherit the `extruder`
  of the object you are extending.

## Color changes

Bambu color tools are for a Bambu 3MF only. U1 colors are the filament slots
in Your setup (navy `#1B2A4A`, cream `#F3EEE0`, unless the job says otherwise).
Kobra colors are separate STLs. The Kobra has no cream loaded.

- **Plain color assignment on a Bambu 3MF**: `scripts/bambu_3mf.py set-color`.
- **Existing project 3MFs** carry paint and settings in `Metadata/`.
  Geometry-preserving edits (uniform scale, move, rotate) go through
  `scripts/bambu_3mf.py transform`, which edits vertices in place inside the XML
  and keeps everything else byte-identical — paint survives. Adding geometry
  goes through `project_3mf.py`. Topology-changing edits lose paint; warn first.
- Splitting one object into color regions with no existing paint: boolean-split
  into bodies, export as multi-object 3MF, one color each.
- Read `references/3mf_bambu_format.md` before hand-editing any 3MF XML.

## Other common edits

- **Resize magnet holes** (D6×3 → D8×3): boolean-cut the new cylinder; if
  shrinking, plug then re-cut. 0.1–0.2 mm diameter clearance for press-fit PETG
  unless the original's measured clearance says otherwise.
- **Add magnet holes**: confirm position, size and depth; keep ≥0.8 mm floor
  between magnet and outer surface if it should be hidden.
- **Mirror / rotate / translate / split / merge / repair**: standard trimesh;
  always re-verify watertightness after booleans.
- **Cut for build plate**: if a scaled model exceeds the target printer's bed
  (`references/jeff_printers.md`; `fits_bed` from `scripts/mesh_info.py`), offer
  to section it with alignment features (dowels or the magnets he actually has).

## Print log and troubleshooting

Print troubleshooting is only cheap the second time. The first time PETG lifts
off the bed you spend an evening on it; the fifth time should take thirty
seconds — but only if the first four were written down. Jeff's record is
`print-log.md` in the designs repo, and the point is to *use* it.

### Retrieve before you advise

**Read the designs-repo print log before answering any settings or
troubleshooting question.** It is `print-log.md` in
`https://github.com/jlmodell/grokalok-jmo-3d-designs` (seeded copy:
`seed/designs-repo/print-log.md`). The bundled `printlog.py` JSON file is not
his log. Do not start a second one.

```bash
# from a clone of jlmodell/grokalok-jmo-3d-designs
# read print-log.md, then append one entry after a real result
```

Read the matching entries, not a summary of the whole hobby. Group what the
successful prints actually used, and separate a value that keeps showing up
from one that changed every time. A consistent value is a finding. A varying
one means that knob probably was not what mattered. His PETG default in the
setup block is 245/70. Do not quote an example from some other shop.

"The log already has a fix for this material and this failure" is a real
answer. Suggesting he dry the filament when the log shows he already fixed
exactly this, a different way, is worse than useless. **If the log holds a fix
matching this material and nozzle, that is the first thing to try, and say so
plainly.** Then add ideas beyond it. If the log is silent, say that too, then
work from `references/troubleshooting.md` and `references/jeff_materials.md` —
and append the eventual fix so next time is cheap.

### Record without ceremony

Append one entry to `print-log.md`, and put the same facts in that version's
`NOTES.md`. Copy the heading shape already in the file. A sparse entry beats
no entry. Log what is known. Do not interrogate him for fields he did not
volunteer. When he says a part finally came out clean, log it and confirm in
a sentence.

The fields worth chasing, in the order they turn out to matter:

1. **Result and issue** — `success`, `partial`, or `fail`, plus what went
   wrong. One print can have several issues. Keep tags consistent:
   "stringing" and "strings" will not find each other later.
2. **Fix** — what actually solved it. When a print succeeds after a failure,
   ask what changed and write it down.
3. **Material, nozzle, layer height** — the three axes most problems sort
   along.
4. **Temps, supports, adhesion, and whether the filament was dried.** Printer,
   if he named it. Leave it unknown if he did not.

Also drop his print photos into `designs/<project>/vN/images/` and embed them
in `NOTES.md`.

Log what he reports and what you measured. There is no required printer
connection to fill the entry. A finished print is the natural moment to offer
it — one line, not a form.

### Where the log lives

In the designs repo, as `print-log.md`, next to `designs/`. Read it from the
clone. Append one entry per result, same shape as the entries already there:
model, printer, material, result, issue, fix, and **PROVEN** / **FAILED** /
**UNTESTED**. Leave the printer as unknown when nobody named it. A starter
log of 18 transcripts is already in that file (and in
`seed/designs-repo/print-log.md`).

`scripts/printlog.py` still reads and writes a local JSON log if you point
`--log` at one. That is a scratch tool. Jeff's history is the markdown file.
Google Drive "3D Prints" is a backup of the design files, not a second log to
maintain by hand.

The markdown is plain on purpose. He can open it and fix a typo without any
tooling.

### Advising a fix

Both of these come from `references/troubleshooting.md`, which maps symptoms to
causes with material-specific sections:

- **Change one thing at a time.** Someone who changes temperature, speed and
  retraction together and gets a good print has learned nothing, and the log
  entry is worthless. Recommend the single highest-probability change first.
- **Prefer the cause over the symptom.** Raising temperature to fix layer
  adhesion when the real cause is wet filament produces a stringy part that
  still delaminates. Ask the diagnostic question — has this been dry-stored? —
  before reaching for a setting. When the MCP is live, `set_ams_drying` can act
  on the answer instead of just advising it.

Filament tracking rides along: the log records material, brand, color and grams,
so `stats` gives total consumption. It is not an inventory system — if the user
wants one, point at Spoolman.

## Hardware dimension lookups

His hardware, and the fits he has already printed, come first:
`references/jeff_workflow.md` and `references/jeff_fits.md`. Design around
those parts. `references/bambu_hardware.md` is only for a Maker's Supply part
he is actually using. For anything unlisted or marked unverified, fetch the
store page or web-search the part number. The mesh's measured dimensions
already include the designer's clearance — preserve *measured* sizes, not
bare catalog sizes.

## Privacy

Never write printer serial numbers, access codes, Bambu account credentials,
cloud tokens, LAN IPs, Wi-Fi details, local usernames, private file paths or
customer/private model names into this skill's files, references, or anything
committed. Treat downloaded private STLs, generated 3MF/G-code, printer logs,
screenshots, MakerWorld session data and any local config file as private —
they stay in the working directory, never in anything shared or published. If
this skill is ever published or shared, secret-scan it first and confirm only
placeholders remain. Use placeholders:
`<printer-lan-ip>`, `<printer-serial>`, `<access-code>`, `<output-dir>`. If
MakerWorld login is needed, use an existing browser session — never ask for
credentials in chat, never store them in a file.

## Failure modes to avoid

- Scaling magnet/hardware holes along with the body (the whole point).
- Booleans on non-watertight meshes — repair first.
- Silently converting a painted project 3MF through trimesh and handing back a
  stripped file.
- Trusting catalog dimensions over measured ones.
- Delivering STL when the standing preference is 3MF, or a renamed copy when
  the user asked for their file edited.
- Fabricating a printer profile so a slicer will run.
- Promising an OpenSCAD, OrcaSlicer-CLI or printer-MCP path before checking it
  is live — preflight for the CLI and local binaries, `ListConnectors` for MCPs.
- Guessing `bambu_model`, or treating this install as an H2C. Bambu models
  are only `a1`, `a1mini`, and `x1c`, and only when a Bambu tool is live.
- Requiring Bambu's printer tool before you deliver a file.
- Delivering a Bambu 3MF to the Kobra X, or an STL as the only file for a
  Bambu printer or the U1.
- Saving a design without `NOTES.md` and a preview image, or deleting an old
  revision before he OKs the print and confirms the list.
- Marking an untested or failed print as proven, or mixing the studio charm
  spec with the Charm bot's tested numbers.
- Using the MCP's `scale_stl` on a model with hardware interfaces — it scales
  the holes too. `scripts/smart_scale.py` first, then slice.
- Starting a print without confirming it with the user.
- Answering a settings or troubleshooting question without checking the print
  log first, or fixing a print and not logging what worked.
- Recommending three changes at once, so the log entry can't say which worked.
- Designing a multi-part assembly here instead of handing it to cad-khana, then
  discovering the fit problem after it printed.
- Trusting a render over a cross-section.
- Lofting rings with a zero-length extension — duplicate rings at the same z
  make manifold3d reject the solid with "Not all meshes are volumes". Same
  error appears when a loft's winding is inconsistent; call `fix_normals()`.

## Adding lessons

A lesson about a *print* — symptom, cause, fix — goes in the designs-repo
`print-log.md`, and in that version's `NOTES.md`. A lesson about the *process*
goes in the matching `references/jeff_*.md` file (or the general reference it
belongs to), tight: failure mode → root cause → fix → why it matters. Keep the
**FAILED** and **UNTESTED** labels. Do not invent a result.
