# Jeff's printers

Defaults live in the "Your setup" block in `SKILL.md`. This file is the fleet
detail. Labels:

- **PROVEN** — Jeff printed it and said it worked.
- **FAILED** — Jeff printed it and it failed.
- **UNTESTED** — designed or advised, and no print result was found.

Do not invent a printer, a bed axis, or a print result that is not written
here. Do not require Bambu's printer tool. Hand Jeff a file.

## What to hand him

| Printer | Bed | File | Source |
|---|---|---|---|
| Bambu Lab A1 | 256×256 mm. Height was not recorded. | Bambu 3MF | Maker, Karambit, Spool |
| Bambu Lab A1 mini | 180×180 mm. Height was not recorded. | Bambu 3MF | Spool, Scouter, Backplate, Napkin |
| Bambu Lab X1 Carbon | 256×256 mm. Height was not recorded. | Bambu 3MF | Spool |
| Snapmaker U1 | "271 plate." The second axis and the height were not recorded. | Orca-style 3MF with filament slots assigned | Karambit, Croc, Frisbee, Charm |
| Anycubic Kobra X | 260×260×260 mm | STL | Karambit, KobraFiles, AirPod, Kobra.25 |

`scripts/mesh_info.py` reports `fits_bed` for these plates. Ignore any older
H2C fit flag. The check uses the two largest dimensions as the footprint, so
a part does not pass by standing on end. It is axis-aligned: a diagonal fit,
like the croc v5 at 45° on the U1, is not credited. The U1 flag treats the
recorded "271 plate" as 271 mm on both plan axes, because that is all the
transcript gave.

The A1 mini is too small for a lot of his parts. Check before promising it:
200 mm spool flanges, the 177–197 mm scouter, the croc cover, and the backplate
one-plate layout (about 198 mm). The scouter rev4 is 197 mm long, so X1 Carbon,
A1, or Kobra only. **UNTESTED** print.

## Per printer

### Bambu A1, A1 mini, X1 Carbon

- Deliver a Bambu 3MF. `scripts/bambu_3mf.py` and `scripts/project_3mf.py` are
  Bambu Studio helpers. Use them only for these three machines.
- `bambu_model` is `a1`, `a1mini`, or `x1c`. Use that string only if a Bambu
  tool is actually live. Never guess it, and never block the job on that tool.
- The A1 has an AMS lite. The X1 Carbon has an AMS. The A1 template in the
  Karambit work ran 255/80, and the textured PEI plate had to be set by hand.
  The standing material default is still PETG 245/70 on smooth PEI (see
  `jeff_materials.md`).
- The X1 Carbon is the only Bambu of his that ships with a hardened nozzle.
  He says he has put hardened steel nozzles on every printer.
- Bambu says TPU 95A cannot go through the AMS or AMS lite. On the A1 or X1
  Carbon, print TPU alone from the external spool. Multi-material TPU is a U1
  job (Frisbee).
- A combined 3MF made from someone else's project keeps that project's printer
  profile (a P1S, in one Maker job). Tell him to switch the printer and press
  Arrange.

### Snapmaker U1

Four toolheads. This is the machine for multi-material work, including TPU in
one head and other materials in the rest.

- Deliver an Orca-style 3MF (Snapmaker Orca) with filament slots assigned.
- Default slots, from Karambit memory: filament 1 is navy `#1B2A4A`, filament
  2 is cream `#F3EEE0`.
- Each printable piece is its own named object. Name color parts
  (`Zombie_shirt_blue`).
- Exception: a piece made of two materials that must stay bonded (TPU + PETG
  or PLA) is ONE object with a part per material, so beam interlocking can
  act. See `multimaterial_interlock.md`.
- Do not hand the U1 a Bambu Studio project and call it an Orca file. Do not
  invent a machine profile, start G-code, or purge routine. Slot assignment is
  filament index and color, not a fabricated printer profile.
- The U1 handoff says textured PEI, and PETG 245/70. The standing bed default
  is smooth PEI; TPU on smooth PEI has its own warning in `jeff_materials.md`.
- He prints big parts diagonally. The croc v5 fit at 45°.
- **UNTESTED** (advised, U1): toolhead "bouncing" on tiny circles such as
  stitch holes is normal Z-hop. Set Z-hop to "only over printed surfaces,"
  0.2–0.4 mm for PETG. Turn on avoid crossing walls. Raise the minimum travel
  before retraction to 1–2 mm.

### Anycubic Kobra X

Four slots, loaded with dark blue, gold, brown, and white. No cream. It has a
0.25 mm hotend as well as the usual 0.4 mm nozzle. Cloud slicer needs STL.

- Deliver STL. That is the standing handoff.
- Anycubic Slicer Next freezes on heavy 3MF imports (KobraFiles). The
  workaround used there: one 3MF, one plate, separate named objects; decimate
  only the decorative meshes (about −38% triangles), never the joints; also
  ship a geometry-only (settings-free) 3MF plus one STL per color. Prefer the
  STL handoff unless he asked for that extra 3MF.
- **FAILED** (Kobra.25): a 0.25 mm job would not send because the nozzle size
  did not match. Set the nozzle to 0.25 on the touchscreen, choose the 0.25
  preset in Anycubic Slicer Next, and re-slice. No successful reprint was
  recorded.
- Guidance given with that 0.25 job, not a confirmed good print: PETG at
  2–4 mm³/s, 0.08–0.15 mm layers, 0.25–0.30 mm line width. Outer walls around
  30 mm/s. Turn Arachne walls on so fine fins print. Dry the filament. The
  test piece was a fine-detail mini Benchy (tiny text, thin walls, pins) plus
  a test with a 0.3 mm fin and a 0.5 mm pin (stretch goal).

## Fit the plate, then the file

Napkin plates were laid out per printer: single-set plates for the A1 mini,
multi-set plates for the Kobra X (260 mm bed). Split long jobs per design.
Use per-plate files when a multi-plate layout might not come through.
