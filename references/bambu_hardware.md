# Bambu Maker's Supply hardware reference

The user builds with Bambu Lab Maker's Supply parts. Interfaces to these parts
must survive scaling and edits at their original physical size.

## Ground rule: the mesh beats the catalog

A well-designed model already includes the designer's fit clearance. When
detect_features.py measures a 6.15 mm hole near a "D6 magnet" candidate, the
correct preserved size is **6.15 mm** (nominal 6.0 + 0.15 clearance), not 6.0.
Preserve measured dimensions; use the catalog only to *identify* what a
feature is and to sanity-check.

## Verifying dimensions at runtime

Dimensions marked (verify) below were not confirmed against official specs.
When a job depends on one:

1. Fetch the Bambu store product page: https://us.store.bambulab.com/collections/makers-supply
2. Web-search `"<PART-NUMBER>" site:makerworld.com` — every Maker's Supply
   part has an official MakerWorld page with dimensions and downloadable CAD.
   (e.g. `"MH011" site:makerworld.com`)
3. Maker's Supply publishes exact digital models of its parts — download the
   CAD/STEP/STL from the part page and measure it directly when precision matters.

## Clock movements

- **MH011 Clock Components Kit** (~$8, for the Maker World Clock): standard
  quartz movement, AA battery, metal hands, hex socket nut, rubber + metal
  washers. Body is the standard ~56×56 mm square movement (verify).
  Mounting is via the threaded shaft bushing through a face hole — typical
  quartz bushings are ~⌀9 mm threaded, face-hole in prints ~⌀9.2–10 mm
  (verify against the actual model's hole; the Maker World Clock face hole is
  the ground truth when scaling that model). Face thickness limit: the bushing
  thread length caps how thick the clock face can be (~3–5 mm typical) —
  **when scaling a clock, warn if the face around the shaft hole gets thicker
  than the original**; keep a recessed boss at original thickness if needed.

## Magnets (Bambu store carries these lines)

- Round/disc magnets — common print sizes D5, D6×2, D6×3, D8×3, D10×3.
- Disc countersunk hole magnets — **12×3×3 mm and 10×4×3 mm** (OD × hole × thick).
- Rectangular magnets — measure the pocket; rectangular pockets are NOT
  auto-detected by detect_features.py (it only finds cylinders). Check for
  small rectangular pockets manually when the user mentions magnets.
- Press-fit clearance in PETG: holes typically designed +0.1 to +0.2 mm on
  diameter, depth = magnet thickness + 0.0 to +0.2 mm. Glue-in designs run looser.
- Magnet **depth matters**: a D6×3 pocket must stay 3.x mm deep after scaling
  or the magnet sits proud/too deep. smart_scale.py preserves blind-hole depth
  by default — keep it that way for magnets.

## Bearings (verify exact SKUs on store)

- 608 (skateboard): 8 ID × 22 OD × 7 mm — the most common in maker models.
- MR128: 8 × 12 × 3.5 mm. 6701: 12 × 18 × 4 mm. (verify)
- Bearing seats: press-fit OD pockets usually +0.0 to +0.1 mm; shafts into
  bores usually −0.05 to −0.1 mm. Both the pocket AND any printed shaft
  (protect as `boss:`) must be preserved when scaling.

## Screws, nuts, inserts

- Maker's Supply fastener kits are mostly M2/M3 (self-tapping and machine).
- Thread-forming holes: M2 → ⌀1.8–2.0, M3 → ⌀2.7–2.9. Clearance: M3 → ⌀3.4.
- M3 heat-set inserts: hole ⌀4.0–4.6 depending on insert (verify).
- Hex-nut pockets: M3 nut = 5.5 mm across flats (pocket ~5.6–5.8), 2.4 mm thick.
  Hex pockets are not cylinders — detect manually.

## Electronics & motion (dims all verify-at-runtime)

- CyberBrick modules, servo motors (MG90S-pattern mounts are common),
  electric push rod LA011, COB LED strips (real diameter ≈1.6–1.9 mm despite
  the 1 mm listing — channel profiles matter), power boards.
- For any of these, download the official CAD from the part's MakerWorld page
  rather than trusting numbers here.

## Printer & material context

- **H2C**: build volume ≈325×320×325 mm (left nozzle only), ≈300×320×325 mm
  dual-nozzle; right nozzle loses ~20 mm in X. 350 °C max nozzle, heated
  chamber. Specs: https://bambulab.com/en/h2c/specs
- **Bambu PETG Basic**: slicer profile handles shrinkage — never pre-compensate
  geometry. For fits: PETG is slightly more elastic than PLA; press-fits
  designed for PLA usually work, but tight snap-fits may need +0.05 mm.
  Minimum reliable wall around a preserved hole: ~1.5 mm (2 perimeters at 0.42).
