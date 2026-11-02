# Multi-material interlock (soft + rigid that stays together)

Use this on **every** part where two materials have to stay bonded: TPU 95A
or softer with PETG or PLA, charms, grips, keychains, gaskets on a rigid
frame. The default is **both** layers at once:

1. a **designed-in mechanical lock** (`scripts/mm_interlock.py`), which holds
   even if the plastics never fuse, and
2. **slicer beam interlocking**, set so it actually generates beams.

Labels: **PROVEN** (printed by Jeff), **FAILED**, **UNTESTED**. Every number
below that is not marked PROVEN is **UNTESTED on his printers** until the
coupon plate (below) has been printed and scored. Record the result in the
designs-repo `print-log.md` and update this file.

## Why PETG kept peeling off TPU (check these first)

Each of these causes a "peels right off" result, even with interlocking on:

1. **Separate objects.** Beam interlocking only works between *parts of one
   object*. Two objects that touch get no beams at all (Bambu wiki). The
   skill used to say "each piece is a separate named object". For a bonded
   piece, that is wrong. Each bonded piece is **one object with one part
   per material**.
2. **Boundary avoidance on a thin part.** The default avoidance is 2 cells,
   and it applies in X, Y **and Z**. A cell is 2 × beam width wide and
   2 × beam layers tall: 1.6 mm × 0.8 mm at the defaults with 0.2 mm layers.
   Sliced here in Bambu Studio 02.08 (A1 profile, 0.2 mm layers) on the
   butt-joint coupon:

   | Strip thickness | Avoidance 2 (default) | Avoidance 1 | Avoidance 0 |
   |---|---|---|---|
   | 1.6 mm (charm-like) | **no beams at all** | beams on 4 of 8 layers | beams on all 8 layers |
   | 3.0 mm | beams on 4 of 15 layers | 12 of 15 | 15 of 15 |

   So a 1.6–3 mm charm with default settings gets close to zero interlock.
   That matches "I turned interlocking on and it still peeled".
3. **PETG laid onto TPU** (a stacked, horizontal interface) at normal PETG
   speed and cooling. **FAILED** for Jeff ("pills of PETG", Backplate). The
   TPU underneath is soft and moves, and a cold, fast PETG bead does not wet
   it.
4. **Wet TPU.** Steam at the interface ruins bonding. Dry before every
   multi-material job.
5. **A gap between the two bodies.** Even 0.05 mm means two walls side by
   side with no fusion. `apply_lock` builds the bodies from one boolean, so
   the shared boundary has zero gap and zero overlap. Check imported meshes
   with `verify_pair`.
6. **A height-range modifier over the interface.** On a Prusa forum
   PETG/TPU part, a height-range modifier stopped the interlock from
   generating in that region. Keep modifiers off the interface layers.

## Which method when

| Situation | Primary lock | Slicer beams |
|---|---|---|
| Side by side, both starting on layer 1 (keychain style) | **Buried dovetail seam** (`dovetail_seam`, z between `cover` and top − `cover`). Optional rigid pins. This is the **PROVEN** Keychain v10 layout. | On. Avoidance per the thickness table below. |
| Rigid art on a TPU base (charms, badges) | **Sink the art** (0.6–0.8 mm, already the charm spec) **+ mushroom pegs** from the art down into the base (`mushroom_peg`). A peg head is captured under TPU even if PLA/PETG never fuses. | On. The sunk walls give the beams a vertical interface. |
| TPU on top of a rigid plate (soft grip pad, bumper on a frame) | **Rivets**: TPU flows down through bores in the plate and caps in a counterbore (`rivet`). TPU printed onto PETG fuses well (Tom's3D). | On. |
| Tiny islands (< 3 mm across, specks, outlines) | None fits. **Do not** rely on bond. Merge into chunky regions ≥ 3 lines wide or drop them. Silk-gold specks **FAILED**. | Will not generate in a feature that small. |
| PLA + TPU | PLA bonds poorly to TPU (Tom's3D; Bambu wiki says avoid TPU+PLA where it is structural). Mechanical lock is **mandatory**, not optional. Jeff's PLA-on-TPU 95A cup charm is **PROVEN** with sunk art. | On (Snapmaker lists TPU+PLA as bondable *with* beams). |
| PETG + TPU | Bonds best of the pairs (Tom's3D, Bambu wiki, Snapmaker). Still lock it, because Jeff's PETG-onto-TPU **FAILED**. | On. |
| ABS / ASA / PC + TPU | Not recommended for structural bonding (Snapmaker). Use a mechanical lock only, or a glued two-piece. | Optional. |

Geometry rules that always apply:

- **Prefer vertical (side-by-side) interfaces that start on layer 1.** Avoid
  large flat areas of PETG printed onto TPU. If the rigid part has to sit on
  TPU, sink it into a pocket, so most of the contact is vertical walls, and
  peg it.
- **Bury the lock.** Keep the soft material at least `cover` (0.8 mm at 0.4)
  clear of the top and bottom faces, so the lock is captured in Z too.
  Keychain v10 stopped TPU 1.2 mm (6 layers) under the top.
- **Minimum lock feature is 3 lines wide** (`min_wall`). Anything thinner is
  either not printed or is a single bead that tears off.
- **Chunky regions.** Each colour region has to be large enough to hold at
  least one lock feature plus `min_wall` all round.

## Designed-in lock defaults (`mm_interlock.LockSpec`)

Line widths are the Bambu/Orca defaults for each nozzle (0.42 for a 0.4
nozzle). Every size is a whole number of lines or layers, so the slicer can
draw it. The undercut is 0.6 mm at 0.4 (about 1.5 lines): big enough that a
TPU 95A head cannot pop through, small enough to fill without voids.

| Feature | 0.4 nozzle (0.2 layer, 0.42 line) | 0.2 nozzle (0.1 layer, 0.22 line) |
|---|---|---|
| min wall around a feature | 1.2 | 0.66 |
| cover (soft skin over a buried lock) | 0.8 (4 layers) | 0.5 (5 layers) |
| mushroom peg neck / head Ø | 2.4 / 3.6 (0.6 undercut) | 1.4 / 2.2 (0.4 undercut) |
| peg head height / pitch | 0.8 / 6.0 | 0.5 / 3.6 |
| dovetail neck / head / depth / pitch | 3.0 / 4.6 / 3.0 / 8.0 | 1.6 / 2.6 / 1.8 / 4.6 |
| rivet bore / cap Ø / cap depth / pitch | 2.0 / 3.6 / 0.6 / 6.0 | 1.2 / 2.2 / 0.4 / 3.6 |

Basis: the PROVEN Keychain v10 geometry (a dovetail plus pins sized for a
0.4 nozzle) and 2.4 mm charm stitch holes. Below roughly 5 lines, a soft
neck prints as a single bead. **UNTESTED** as numbers: print the coupon.

**0.2 nozzle and TPU.** Snapmaker does not recommend a 0.2 nozzle for TPU
90A (high extrusion resistance, clogging). Print the TPU part with a 0.4
nozzle. Use the 0.2 set only when the soft material really is going through
a 0.2 nozzle (Kobra X 0.25: use `LockSpec.for_nozzle(0.25)`, which scales
the 0.4 set and prints an UNTESTED warning).

## Slicer settings (Bambu Studio, OrcaSlicer, Snapmaker Orca)

Settings are under Process → Others → Advanced (Bambu wiki: "Global →
Others → Advanced"). The key names are identical in Bambu Studio and Orca
`PrintConfig.cpp`.

| Key (UI label) | Default | Use |
|---|---|---|
| `interlocking_beam` (Use beam interlocking) | off | **on** |
| `interlocking_beam_width` (Interlocking beam width) | 0.8 mm | **0.8** for a 0.4 nozzle. Try 1.0–1.2 on the coupon, because softer material wants a wider beam (CuraEngine PR #1575 notes). For a 0.2 nozzle use **0.44–0.6**. The Bambu wiki says 0.4–0.8 suits small parts and 0.2 is too weak. |
| `interlocking_orientation` (Interlocking direction) | 22.5° | leave |
| `interlocking_beam_layer_count` (Interlocking beam layers) | 2 | **2** (Bambu wiki: keep at 2) |
| `interlocking_depth` (Interlocking depth) | 2 cells | **2**. More than 2 adds no strength (CuraEngine PR #1575) and adds tool changes. |
| `interlocking_boundary_avoidance` (Interlocking boundary avoidance) | 2 cells | **2** at ≥ 5 mm thick. **1** at 2.5–5 mm. **0** under 2.5 mm (charms). 0 lets beam ends show on the side walls. That is cosmetic; accept it on a charm edge. |
| `mmu_segmented_region_interlocking_depth` | 0 | leave. It is ignored when beams are on. |
| `interface_shells` (Interface shells) | off | leave off. It forces solid shells at every material boundary. Beams do the job; only try it on the coupon if beams cannot generate. |

Process and temperature, all **UNTESTED** starting points:

| Pair | Soft (TPU 95A) | Rigid | Interface |
|---|---|---|---|
| PETG + TPU 95A | 225–235 °C, 20–30 mm/s (Keychain v10 used ~20 mm/s, **PROVEN**), fan per profile | PETG 245 °C default. Raise to 255 °C for this job; a Prusa forum PETG/TPU fix needed ~265 °C. Fan ≤ 30–40%. | Outer and inner walls ≤ 50 mm/s on both. Prime tower on, brim on, Z-hop on (Keychain v10). |
| PLA + TPU 95A | same | PLA 215–220 °C, fan normal **after** layer 3 | Mechanical lock required. Sink and peg the art. |
| TPU 75–85A | 215–225 °C, 15–20 mm/s | as above | Buckles in feed paths (85A may buckle in the U1, **UNTESTED**). Make the lock one step stronger: pitch × 0.8, undercut +0.2 mm (a judgement call, not from a source). |

Also:

- **Dry the TPU** before every multi-material job: 70 °C for 6 h
  (Snapmaker TPU 90A, already Jeff's U1 note), or 75 °C for 18 h for TPU
  95A HF (Bambu H2D guide).
- **Purge.** Prusa recommends ~35 mm³ when switching to TPU, up to 70.
  Snapmaker Orca and Bambu flush values cover this. Do not lower them.
- **Bed.** Textured PEI (or glue) for anything with TPU on layer 1. Smooth
  PEI can bond TPU hard enough to tear (Jeff, Keychain).
- **Where it runs.** TPU cannot go through a Bambu AMS or AMS lite, so a
  TPU + rigid job is a **U1** job. Bambu A1/X1C slicer settings are only for
  rigid-rigid pairs.

## Workflow (default for any multi-material part)

1. Design each body in build123d. Choose the lock from "Which method when".
2. `owner, other = apply_lock(owner, other, features)`. The rigid body owns
   pegs and dovetails; the soft body owns rivets.
3. `verify_pair(a, b)` must pass: overlap ≈ 0, union is one solid.
4. `export_parts_3mf(path, [("body_TPU", soft, 1), ("art_PLA", rigid, 2)])`.
   This writes **one object, one part per material**, with filament slots in
   `Metadata/model_settings.config`. Bambu Studio 02.08 loads it as one
   object with 2 parts on extruders 1 and 2 (checked). It also writes STLs
   for the Kobra X: import them together and choose "single object with
   multiple parts".
5. In the slicer, set the beam keys above, then **look at the preview**: a
   checkerboard of both colours at the seam means beams were generated.
   If the seam is a clean line, there are no beams. Lower the avoidance.
6. First time for a material pair, nozzle or printer: print the coupon plate.

## Coupon plate (`scripts/interlock_coupon.py`)

```bash
python scripts/interlock_coupon.py --nozzle 0.4 --out <output-dir>
python scripts/interlock_coupon.py --nozzle 0.2 --out <output-dir>
python scripts/interlock_coupon.py --only butt --thickness 1.6 --out <output-dir>   # thin-charm control
```

One 3MF with five objects (two parts each: soft = slot 1, rigid = slot 2;
change with `--soft-slot` and `--rigid-slot`), plus per-part STLs. Count the
notches to tell coupons apart:

| # | Coupon | What it tells you |
|---|---|---|
| 1 | butt (side by side, straight seam) | Slicer beams alone. Print once with avoidance 2 and once with 0 to see the difference. |
| 2 | dovetail (buried) | Side-by-side lock (keychain layout) |
| 3 | pegs (rigid plate sunk 0.8 into a 3.0 mm base, mushroom pegs) | Art-on-base lock |
| 4 | flat (same stack, no pegs) | Control for 3 |
| 5 | rivet (TPU rivets through the plate) | Soft-over-rigid lock |

Score each one, then log it:

1. Bend it 10 times to 90° by hand.
2. Twist it ±90° 10 times.
3. Pull the side-by-side strips by the holes (pliers, or hang a weight).
4. Pry the stacked plates with a fingernail, then with a flat screwdriver.

Write down for each coupon: holds / partial / peels, and where it failed
(at the interface, or tore through the TPU). A "tore through TPU" failure is
the goal: the joint is stronger than the soft material.

Slice check done while building this (Bambu Studio 02.08 CLI, A1 profile,
two filament slots): all five coupons load as one object with two parts.
The pegs and rivets show up as the right material at the right heights.
Beams generate with avoidance 0, 1 and 2 on the 3 mm strip, and only with
0 or 1 on the 1.6 mm strip. Not printed yet: **UNTESTED**.

## Sources

- OrcaSlicer `src/libslic3r/PrintConfig.cpp` and BambuStudio
  `src/libslic3r/PrintConfig.cpp`: key names, labels, defaults (identical).
- BambuStudio `src/libslic3r/Interlocking/InterlockingGenerator.{hpp,cpp}`:
  cell = 2 × beam width by 2 × beam layers. Air dilation removes cells
  near the outside in all three axes.
- Bambu Lab wiki, "Beam Interlocking in Bambu Studio"
  (wiki.bambulab.com/en/software/bambu-studio/beam-interlocking): single
  object only, keep beam layers at 2, check wall thickness, TPU+PETG bonds
  and TPU+PLA does not.
- Bambu Lab wiki, "H2D Soft and Hard Filament Multi-Material Printing
  Guide": TPU 95A HF drying 75 °C / 18 h, beams on for rigid + TPU.
- Ultimaker CuraEngine PR #1575 (the original interlocking generator):
  horizontal beams alternating 90° per beam layer, depth > 2 adds nothing.
- Snapmaker wiki, "TPU 90A Filament": TPU bonds with PLA, PA, PETG and PET
  with beams; not ABS, ASA or PC; dry 70 °C / 6 h; 0.2 nozzle not
  recommended for TPU.
- Tom's3D, "Try these filament combinations for Multi-Material and
  Supports" (2024-12): PETG and flex fuse very well both ways; PLA bonds
  poorly to TPU and PETG.
- Prusa forum (PETG/TPU interlock thread): PETG at ~265 °C and ~50 mm/s, and
  a height-range modifier suppressed the interlock. Prusa XL knowledge base:
  TPU purge ~35 mm³, up to 70.
- Jeff's own results: `jeff_materials.md` (Bonding table) and
  `jeff_design_rules.md` (Keychain v10).
