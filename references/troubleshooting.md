# FDM troubleshooting

Symptom → likely causes, ordered by how often each is actually the culprit.
Change one variable at a time, and log what worked.

## Contents

- [Bed adhesion / warping](#bed-adhesion--warping)
- [Stringing and oozing](#stringing-and-oozing)
- [Layer adhesion / parts snapping](#layer-adhesion--parts-snapping)
- [Under-extrusion](#under-extrusion)
- [Supports that won't come off](#supports-that-wont-come-off)
- [Surface quality](#surface-quality)
- [Dimensional accuracy](#dimensional-accuracy)
- [Multi-material and color bleed](#multi-material-and-color-bleed)
- [Material-specific notes](#material-specific-notes)
- [The wet filament question](#the-wet-filament-question)

## Bed adhesion / warping

1. **Dirty bed.** Skin oils are the number one cause and the easiest to rule
   out. Wash the plate with dish soap and hot water — not just isopropyl, which
   smears oils around rather than removing them.
2. **Wet filament.** Especially PETG, nylon, TPU. See below.
3. **Bed temp too low** for the material, or **first layer too fast**.
4. **Nozzle too high** on the first layer. The first layer should look slightly
   squished, not round beads sitting on the plate.
5. **Warping from thermal contraction** — large flat parts in high-shrinkage
   materials. Fix with a brim, an enclosure, or a lower bed-to-nozzle temp delta.
6. **Wrong plate for the material.** PETG sticks aggressively to smooth PEI and
   can pull chunks out of it; use a textured plate or a glue-stick release layer.
   Glue on PETG is about *preventing* over-adhesion, which surprises people.
7. **Draft.** An open printer near an AC vent warps large parts.

**Brim vs raft**: a brim solves corner lifting and costs little. A raft solves an
uneven bed and costs a lot of time and material. Try the brim first.

## Stringing and oozing

1. **Wet filament.** The single most common cause. Moisture flashes to steam and
   sprays material. If a spool has sat out for weeks, dry it before changing any
   setting.
2. **Temperature too high.** Drop in 5 °C steps and print a retraction tower.
3. **Retraction distance or speed too low.** Direct drive needs far less
   retraction (0.5–2 mm) than Bowden (4–7 mm). Over-retracting causes its own
   problems — clogs and under-extrusion at travel starts.
4. **Travel speed too slow** — faster travels give the ooze less time to form.
5. **Missing "wipe" or "retract on layer change."**
6. **Flexible filament (TPU, PEBA)** strings much more readily and tolerates less
   retraction because the filament stretches instead of pulling back. Rely on
   temperature and travel speed here rather than retraction distance.

## Layer adhesion / parts snapping

1. **Temperature too low.** Layer adhesion is the one problem where *more* heat
   is usually right. Go up in 5 °C steps.
2. **Cooling too aggressive.** PETG, ABS, ASA, and nylon all want minimal part
   cooling. Full-blast fans on PETG guarantee weak layers.
3. **Wet filament** — moisture disrupts the melt bond.
4. **Layer height too large for the nozzle.** Keep layer height under ~75% of
   nozzle diameter.
5. **Under-extrusion** — see below.
6. **Print orientation.** FDM parts are weakest across layer lines. If a part
   snaps along a layer, the fix may be reorienting it rather than any setting.

## Under-extrusion

1. **Partial clog.** Cold pull, or push filament by hand at temp and feel for
   resistance.
2. **Extruder tension** too loose, or a worn drive gear.
3. **Temperature too low** for the speed — the hotend can't melt fast enough.
   Either slow down or heat up.
4. **Flow rate calibration** off — run a flow calibration.
5. **Filament diameter variation** on cheap spools.
6. **Tangled spool** creating drag. Check the spool, not the printer.

## Supports that won't come off

1. **Z gap too small.** This is almost always it. The top Z distance between
   support and part should be roughly one layer height for rigid materials; with
   a 0.6 mm nozzle at 0.12 mm layers, gaps well north of 0.4 mm are workable.
   Larger nozzle, larger workable gap.
2. **Wrong support type.** Tree supports touch less surface and peel off far more
   easily on organic shapes. Normal supports are better under flat overhangs.
3. **Support interface layers** — a dense interface improves the surface finish
   but makes removal harder. Reduce interface density, or add a small interface
   gap.
4. **Flexible materials weld to their supports** regardless of settings. With
   PEBA or TPU, design the part to avoid supports, print in a different
   orientation, or use a soluble interface if the printer supports it.
5. **Overhang angle** — anything over about 45° may not need supports at all.
   Check before adding them.

## Surface quality

**Ringing / ghosting** — echoes after sharp corners. Reduce acceleration and
jerk, tighten belts, make sure the printer sits on something solid. Input shaping
calibration if the firmware has it.

**Z banding** — horizontal bands at regular intervals. Bent lead screw, binding
Z axis, or inconsistent extrusion. Check whether the band spacing matches the
lead screw pitch.

**Elephant foot** — bulging first layer. Nozzle too close, bed too hot, or too
much first-layer flow. Most slicers have an elephant-foot compensation setting.

**Blobs and zits** — seam placement and coasting. Set the seam to "aligned" or
hide it on an internal corner. Enable coasting or wipe.

**Visible seam line** — unavoidable in FDM, but placement is controllable. Align
it to a back edge or a corner, or use "scarf seam" if the slicer offers it.

**Poor bridging** — increase cooling for bridge layers specifically, slow the
bridge speed, and check that bridge flow is under 100%.

## Dimensional accuracy

1. **Elephant foot** at the base throws off the first few millimeters.
2. **Shrinkage** — every material shrinks on cooling. Roughly 0.3–0.5% for PLA,
   0.4–0.6% PETG, 0.7–0.8% ABS/ASA. For a press fit, print a test coupon rather
   than trusting a number.
3. **Over-extrusion** makes holes small and outer dimensions large. Holes are
   almost always undersized in FDM — design them oversized or plan to drill.
4. **Horizontal expansion / XY compensation** in the slicer corrects a
   consistent offset once measured.

For anything with a required fit — magnet pockets, bearing seats, threaded
inserts — print a small test coupon first. It costs ten minutes and saves the
part.

## Multi-material and color bleed

1. **Insufficient purge** between filament changes. Increase purge volume; a
   purge tower or an object used as a purge target reclaims some of the waste.
2. **Dark-to-light transitions** need far more purge than light-to-dark. Order
   the color sequence to go light → dark where the model allows.
3. **Nozzle temp mismatch** between materials on the same print. Where the
   materials differ, the shared temperature is a compromise; check both are in
   range.
4. **Wet filament** worsens stringing across the purge tower, which drags color
   into the part.

## Material-specific notes

**PLA** — easy. 190–220 °C, bed 50–60 °C, full cooling. Brittle over time and in
heat; a PLA part in a hot car will sag.

**PETG** — 230–255 °C, bed 70–85 °C, **minimal cooling** (under 40%). Strings
readily, absorbs moisture readily, sticks to smooth PEI too well. The most common
PETG problems are all traceable to wet filament or too much fan.

**ABS / ASA** — needs an enclosure. 240–260 °C, bed 90–110 °C, cooling off or
nearly off. Warps and delaminates without a stable ambient temperature. Vent the
fumes.

**TPU / flexibles** — slow (20–30 mm/s), minimal retraction, direct drive
strongly preferred. Softer shore ratings are progressively harder to print.

**PEBA** — a flexible engineering material: stronger and more resilient than TPU,
and more demanding. Dry it thoroughly, print slow, keep retraction minimal, and
expect supports to weld to the part — design around supports rather than trying
to tune them out. Best results usually come from reorienting the part.

**Nylon (PA)** — extremely hygroscopic; it absorbs enough moisture in a few hours
of open air to ruin a print. Dry immediately before printing and print from a dry
box. High temp, enclosure, minimal cooling.

**Carbon/glass-filled** — abrasive. Requires a hardened nozzle; a brass nozzle
will visibly wear within a spool or two.

## The wet filament question

Ask about moisture before adjusting settings for: stringing, poor layer adhesion,
rough or bubbly surfaces, popping or crackling sounds during printing, or
inconsistent extrusion. It causes all of these, and no setting compensates for it.

Drying guidance:

| Material | Temp | Time |
|---|---|---|
| PLA | 45–55 °C | 4–6 h |
| PETG | 60–65 °C | 6–8 h |
| TPU / PEBA | 50–60 °C | 8–12 h |
| ABS / ASA | 65–75 °C | 4–6 h |
| Nylon | 70–80 °C | 12+ h |

Keep the temperature below the material's glass transition or the spool deforms
and jams. After drying, store with desiccant — a spool left out re-absorbs
moisture in days, faster in a humid climate.

Symptoms of wet filament while printing: audible popping or hissing from the
nozzle, steam, a rough or foamy extrusion, and stringing that doesn't respond to
retraction changes.
