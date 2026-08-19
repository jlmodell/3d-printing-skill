# Plate arrangement, stacking and batch sessions

Read this whichever print path you are on. The pattern-selection criteria live
in `print_prep.md`'s "Plate arrangement decision tree" section — that file is
the fallback path for *output*, but its arrangement criteria apply equally when
slicing through the Bambu MCP, so go read that section either way. This file
holds the **procedures**: how to execute each pattern.

Pick the densest packing the geometry allows before falling back to separate
plates.

**Who does the arranging depends on the path.** With the `Bambu_Printer` MCP
live, `slice_stl` takes `arrange: true`, `orient: true`, `repetitions` and
`clone_objects`, which covers Pattern C and simple duplication without touching
a UI. Pattern A (vertical stacking) and Pattern B (print-by-object scheduling)
are still Bambu Studio UI operations — neither the MCP nor the bundled scripts
can set them. The step-by-step UI procedures below are for those two.

## Pattern A — vertical stack

Parts physically on top of each other; the lower part's top surface acts as the
bed for the next. Right answer for repeated drawer/bin/lid/tray geometries.

The bundled scripts cannot do this — it is a slicer-UI operation:

1. Drag all stackable parts onto a single plate.
2. Select all → right-click → **Merge** (called "Assemble" in older versions).
   Each object becomes a *part* of one assembly. Bambu Studio only allows
   Z-axis movement on parts, not on standalone objects, which is why the merge
   step is mandatory.
3. Alt+Click (or use the object list) to select each part.
4. Move tool → set Z to `part_height × index`. Three identical 25 mm drawers
   stacked: Z = 0, 25, 50.
5. Slice as normal. The slicer treats the assembly as one tall object with
   correct layer transitions.

Geometric requirements:

- Flat top on the lower part; flat bottom on the upper part.
- Upper part's footprint ⊆ lower part's top (no overhang).
- Total stacked height ≤ printer Z range.
- Same filament across the stack.

If the parts must separate afterwards, the interface has to be an incompatible
material pair: PLA parts → PETG interface, PETG parts → PLA interface. Confirm
the AMS actually has both before generating the file.

*Common disqualifier:* Gridfinity bins have feet rather than flat bottoms and an
open rim rather than a flat top. They never stack for printing.

## Pattern B — sequential print-by-object

Parts side-by-side, each finishing completely before the next starts.
Failure-isolating: if one falls off, the rest continue.

1. Place parts on one plate with at least `extruder_clearance_max_radius` XY
   spacing (read it from the project config, not from memory; with no project
   config to read, ~67 mm is the Bambu ballpark).
2. Process settings → **Special mode** → Print Schedule: **By Object**.
3. Every object printed before another must be shorter than
   `extruder_clearance_height_to_rod` (~25 mm typical if there is no config to
   read), unless it prints last.

## Pattern C — multi-object, same layer

The default and usually the only survivor for tall parts. Everything prints
layer-by-layer with travel moves between objects.

```bash
python scripts/project_3mf.py add-plate --project p.3mf \
    --mesh part-a.stl part-b.stl part-c.stl --extruder 6 --name "Plate" --out p.3mf
```

Shelf-packs with a fixed 15 mm bed margin and 12 mm inter-part gaps; only the
bed size itself comes from the project. Verify everything landed on-bed
afterwards, and widen the constants in `shelf_pack()` if a part needs it.

If a slicer with a real profile is live, its own arrange/auto-orient is fine
too. Watch bed margins on near-bed-sized parts — auto-arrange has been observed
placing large parts partly off the usable area.

When Pattern C carries several tall thin-walled parts, say so: inter-object
travel causes stringing in PETG. Offer retraction-when-crossing-perimeters, or
split across two plates.

## Multi-plate 3MFs handed in

If the user hands over a 3MF with several plates, check whether the plates are
identical before doing anything clever. Identical plates of flat-topped parts
are candidates for collapsing into one stacked plate (Pattern A) and cutting the
session length substantially. Non-identical plates usually are not.

Same instinct at smaller scale: when a single part leaves half the bed empty and
the user is printing more than one of them, offer a two-up plate rather than
silently printing one.

## Batch print night

When the user wants to maximise a print session:

1. Collect all STLs — designed and downloaded.
2. Group by filament type. Never mix PLA and PETG on one plate.
3. Arrange each group with the best pattern its geometry allows.
4. Generate one plate per group, all in a single project 3MF where possible so
   the user opens one file.
5. Send to the printer via `printer_control.md` if that path is live, otherwise
   hand over the 3MF to open in Bambu Studio.

Report the plate order and the estimated filament per plate, so the user knows
what to load and in what order.

## Remixing a downloaded model

Match the source 3MF's own profile rather than imposing defaults — the designer
tuned it. If only an STL is available, inherit the configured defaults from
SKILL.md's "Your setup" block. Bambu Studio shows a harmless version-mapping dialog
when opening an OrcaSlicer-produced 3MF; tell the user to click through it
rather than treating it as an error.
