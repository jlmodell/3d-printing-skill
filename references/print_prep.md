# Print preparation without a slicer

## First: is the Bambu MCP live?

If `ListConnectors` shows the `Bambu_Printer` MCP, **this file is the fallback,
not the plan.** That connector slices (`slice_stl`, `slice_with_template`) with a
real `h2c` machine profile and prints directly — go to `printer_control.md` and
use it. Everything below applies when the connector is absent.

The rule against fabricating a profile is unchanged either way. The MCP path
satisfies it by supplying a genuine profile, not by relaxing it — which is why
`bambu_model: "h2c"` is required on every call and must never be guessed.

## The rule

**Never fabricate a machine profile to satisfy a slicer.** If the installed
slicer has no profile for the user's printer, the honest output is a Bambu
Studio *project* 3MF, not G-code.

Why this is not caution theatre: a machine profile carries bed shape, toolhead
clearance, purge/prime routines, start/end G-code, and — on dual-nozzle
machines — the extruder mapping. Hand-writing one produces a file that slices
without complaint and can drive the toolhead into a printed part hours in. The
user cannot tell good G-code from bad by looking at it, so a confident-sounding
delivery is the dangerous failure mode.

## What was actually observed (2026-08, H2C project)

- OrcaSlicer 2.3.0 Linux AppImage ships **37 BBL machine profiles, none in the
  H2 family**. No H2C. Downloading a slicer does not get you a profile.
- The AppImage binary also needs `libwebkit2gtk-4.1.so.0` and a GL stack, so it
  will not launch in a headless container at all.
- The OrcaSlicer wrapper CLI (`scripts/cli/cli.ts`, from the old `bambu-slicer`
  skill) was absent from the installed skill, so its profile-patching layer — the thing
  that resolves Bambu `inherits` chains and swaps Bambu G-code templates for
  Orca-compatible ones — did not exist to fall back on.
- No `bambu-printer` MCP connector was present, so AMS state, printer status
  and send-to-printer were all unavailable. `ListConnectors` returning `[]`
  is the check; do it before claiming any printer capability.

Run `scripts/preflight.py` rather than assuming any of this is still true.

## The project-3MF path (preferred output)

The user's own project file already contains a correct, complete
`Metadata/project_settings.config`: their printer, their filaments, their
process settings, written by their own Bambu Studio. Adding geometry to that
file yields a print-ready result **by construction** — no profile is invented
at any point.

    python scripts/project_3mf.py add-part  ...   # fuse into an existing object
    python scripts/project_3mf.py add-plate ...   # new plate of new parts

The user opens it, selects the plate, clicks Slice. That is seconds of work and
is correct in a way that remote slicing would not have been.

If the user has no project file to extend (fresh geometry, no source 3MF), emit
a plain 3MF plus a one-line note that they should pick their printer/filament
profile on import.

## Plate arrangement decision tree

Pick the densest packing the geometry actually allows. Read the clearance
values out of `Metadata/project_settings.config` rather than using folklore
numbers — `extruder_clearance_height_to_rod`, `extruder_clearance_max_radius`,
`extruder_clearance_height_to_lid`.

**Pattern A — vertical stack.** Parts physically on top of each other, merged
into one assembly, each part's Z set to `height * index`. Requires a flat top
on the lower part and a flat bottom on the upper one, with the upper footprint
inside the lower top. Right answer for repeated flat trays and lids.
*Disqualifier seen in practice:* Gridfinity bins have feet, not flat bottoms,
and an open rim, not a flat top. They never stack for printing.

**Pattern B — sequential by-object.** Side-by-side, each finishing before the
next starts; failure-isolating. Requires parts shorter than
`extruder_clearance_height_to_rod` (47.4 mm on the H2C project measured) and
spacing of at least `extruder_clearance_max_radius` (96 mm there).
*Disqualifier:* anything tall. 105 mm bins are disqualified twice over.

**Pattern C — multi-object, same layer.** Everything prints together
layer-by-layer. The default, and usually the only survivor for tall parts.
`project_3mf.py add-plate` does this with a shelf packer, 15 mm bed margin and
12 mm gaps.

When Pattern C carries several tall thin-walled parts, say so: inter-object
travel causes stringing in PETG. Offer retraction-when-crossing-perimeters, or
splitting across two plates.

## Filament selection

Do not read the profile's display colour as the user's loaded filament. If a
`bambu-printer` MCP is live, query the AMS and match on material + brand. If it
is not, preserve the source 3MF's filament assignment — for a new part fused
into an existing object, inherit that object's `extruder` value rather than
guessing a slot.
