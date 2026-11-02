# Jeff's materials, plates, and bonding

Standing defaults from his setup: **PETG, 245 °C nozzle / 70 °C bed, smooth
PEI, 0.4 mm hardened nozzle, 0.2 mm layers.** The A1 template used 255/80.
That is a past template, not the default.

Labels: **PROVEN** (printed and it worked), **FAILED** (printed and it
failed), **UNTESTED** (designed or advised, no print result).

Shrinkage stays in the slicer. Do not pre-scale a mesh for it. ABS parts that
sit in the filament dryer use about 100.5% XY compensation in the slicer
(Spool). That is a slicer setting, not a mesh edit.

## Plates

The default bed is smooth PEI.

Other plates he has used or been handed:

- AirPod handoff (Oct 11): a smooth G10 garolite plate with glue stick. PETG
  at a 70–80 °C bed. TPU at ambient.
- U1 handoff (Karambit): textured PEI.
- He has been using smooth PEI with a laser-etched pattern. Glue for TPU is
  "a pain" to clean every time (Charm).
- Charm advice: a textured PEI plate for TPU-first charms, and the etched
  smooth plate for PLA/PETG. Smooth PEI can bond TPU hard enough to tear.
- Keychain v10: TPU can bond very hard to smooth PEI at 70 °C. Use the
  textured plate, or glue under the hinge.

For a TPU-first part, do not treat smooth PEI as safe just because it is the
default. Say which plate and why.

## PETG and the usual profile

- He prints mostly PETG. Final parts for work prototypes are translucent PETG
  or PCTG (AirPod v9 handoff).
- Usual starting layer height is 0.2 mm.
- Multi-color flat pieces on the U1 (bookmarks): 100% infill, no supports
  (KobraFiles).
- Hardened steel nozzles are on every printer (Spool).

## TPU

**Feeding**

- Bambu says TPU 95A cannot go through the AMS or AMS lite. TPU in a
  multi-material job is a U1 job. On the A1 or X1 Carbon, TPU is alone, from
  the external spool (Frisbee).
- 85A may buckle in the U1 feed path. Use 90–95A (Frisbee). **UNTESTED** as a
  print result.
- He wants TPU only sparingly on the U1, as a second material (AirPod
  handoff).

**Settings that were used or advised**

- Frisbee profile: about 225 °C, slow outer walls, dry the filament first.
  The frisbee itself is **UNTESTED**.
- Keychain fix: TPU at about 20 mm/s. v10, which used this, is **PROVEN**.
- **FAILED** — TPU 57D on the U1 (Charm): pilly surface, and PLA barely stuck.
  The profile was built from Snapmaker's "Generic TPU 95A HF @U1": 235 °C,
  fan 100%, textured PEI at 45 °C, max volumetric speed 8 mm³/s. Dry TPU at
  70 °C for 6 h. He leaned toward buying 95A yellow instead. Drying was
  advised. It was not recorded as the thing that fixed a reprint.

TPU-GF (black) was the original base for the charm patches.

## Bonding

| Pair | Result | What to do with it | Source |
|---|---|---|---|
| PETG printed onto TPU | **FAILED.** Beads into "pills of PETG" and will not bond. | Glued two-piece, or a mechanical lock. | Backplate |
| PETG and TPU side by side, both starting on layer 1, buried dovetail, PETG pins | **PROVEN.** Keychain v10 "worked perfectly." | See `jeff_design_rules.md`. | Keychain |
| PETG art on a TPU-GF base | Bonding was a problem on the original patches. v2 sank the art 0.6 mm into the base. | Charm-bot sunk-art approach. | Charm |
| PLA art on a TPU 95A base (U1) | **PROVEN.** Coffee cup charm on an orange base "came out awesome." | Preferred charm pair. | Charm |
| Silk gold PLA, small bits, on TPU | **FAILED.** The small gold pieces fell off. | Drop tiny islands. Use big chunky regions. | Charm |
| PLA on TPU 57D | **FAILED.** Barely stuck. The TPU may also have been wet. | Do not use 57D for this. | Charm |
| PLA support interface on PETG at 0 top-Z gap | **FAILED.** "Didn't come off easily at all." | They switched to HIPS. | Karambit |
| PLA support under TPU | Advised, because PLA barely sticks to TPU. | Frisbee is **UNTESTED**. | Frisbee |
| HIPS under TPU or PETG | Advised. | Karambit numbers below. The profile import is **UNTESTED**. | Karambit, Keychain |

Any bonded soft + rigid part also gets the designed-in lock and beam
settings in `multimaterial_interlock.md`. That file explains why PETG peeled
off TPU even with interlocking on: separate objects, or default boundary
avoidance on a thin part, gives zero beams.

HIPS numbers from Karambit: 235–240 °C, fan 30–50%, support interface only
(2–3 layers), bed stays 70. A "Generic HIPS @U1" Orca profile was made from
Generic ABS (235/240 first layer, 70 bed, 10–30% fan). Import was not tested.

## Other filaments

- **ABS** is for parts that sit in the filament dryer: 100 °C bed, enclosure
  closed, XY shrink compensation about 100.5% in the slicer (Spool).
- Rods: PETG-GF or ABS beat PLA-CF. PLA-CF is stiffer but brittle, with
  weaker layer bonds. Use GF for toughness at dovetails and threads (Spool).
- He never uses ASA. An old roll snapped inside the PTFE tube (Spool).
- PETG-GF in the AMS is fine. Keep the spool dry (Spool).

## Print time

He notices long prints.

- A plate of 9 flexis taking 4 h was acceptable (KobraFiles). A single took
  2 h.
- A 5–6 h croc cover was too long, so it was thinned (−23% volume) (Croc).
- A 6 h combined strap plate was split into one file per design (AirPod).
- A 6 h plate of spring-leaf fins: print only the fin you need, 0.28 mm
  layers, 2 walls, 10% infill (Spool).
- Flexis with multi-color on every layer took "ages." Keep colors to the top
  few layers, or print one design per plate (KobraFiles).

## On hand (mentioned, not a weighed inventory)

PETG in many colors, including navy and cream. TPU 95A, TPU-GF, TPU 57D
(yellow). Silk PLA (gold, copper, silver), PLA. HIPS, ABS, PETG-GF
(considered). Kobra slots: dark blue, gold, brown, white. No cream on the
Kobra.
