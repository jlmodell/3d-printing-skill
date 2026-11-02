# Jeff's fits

Numbers he printed, and the ones that failed. Do not replace these with a
generic 0.2 mm clearance. Labels: **PROVEN**, **FAILED**, **UNTESTED** (no
print result found).

The slicer will fill a slit under about 0.4–0.5 mm. Check the slicer preview,
and turn **detect thin walls** off.

## Sliding and rails

- **PROVEN** — sliding-fit coupon (Karambit): lanes at 0.15 / 0.20 / 0.25 /
  0.30 mm. He said 0.20 and 0.25 were both good. The knife channel used
  **0.22 mm**.
- **FAILED** — Mcon dovetail rail in PETG: 0.18 mm clearance over a 40 mm rail
  jammed.
- **FAILED** — a tight Mcon rail bulged a 1.2 mm roof over the slot.
- Fix that followed: about 0.25–0.30 mm clearance, slot widened 0.15 mm per
  side, roof back to ≥1.5 mm (plate 3.75 mm), detent bumps only on the last
  2.5 mm, elephant's foot compensation ≤0.1 mm.
- The shortened 16.5 mm sliding shelf printed and seated (his photo, Mcon).
  The rail was cut to 16.5 mm because the controller key blocks the slot about
  17 mm in.

## Press and snap

- **PROVEN** — AirPod case-gripping fingers: 0.3 mm per side interference
  "fit perfectly." He asked to "ease off a tad," so v11 went to 0.2 mm per
  side. A print result for that 0.2 mm change was not recorded.
- **FAILED** — a 0.55 mm snap catch "never caught with any strength — fell out
  with any movement."
- **PROVEN** — six catches (4 inner hooks at 1.8 mm plus 2 outer latches)
  "fit perfectly together" (AirPod v10).

## Bearings and the blade pocket

- **PROVEN as his best seat** — 6803 bearing seat at **26.20 mm** with
  **25.88 mm crush ribs** (Karambit).
- **FAILED** — karambit v9: the bearing would not seat flush in its dovetail
  hole.
- Utility blade pocket opened to +0.4 mm all around (20.35 mm wide at the
  floor). An earlier "expanded" pocket missed because the widening started
  0.2 mm above the floor (Karambit).

## Detents

Most of the karambit failures were here.

- Engagement has to exceed side play.
  - **FAILED** — v10: the tab only went 0.17 mm into the notch while the
    slider had 0.22 mm of side play, so it pushed the slider over and never
    clicked.
  - v11: a stiffer 1.5 mm tab, backed up so the slider cannot drift away,
    plus deeper notches. He said it "printed the best of all versions."
- **FAILED** — the slicer filled flex-bar slits of 0.3–0.5 mm, and a 0.25 mm
  gap under a spring strip, so the parts were rigid. Use ≥0.6 mm cuts
  (karambit v6.1 went to 0.6–0.65; v8.1 used a 0.4 gap with a 1.0 mm slit
  behind it).
- Carabiner gate cuts at 0.35 mm fused. 0.55–0.6 mm is OK.
- Turn "detect thin walls" off, and check the slicer preview (Karambit,
  Carabiner).
- Loose ball-and-spring detents are a no. He lost about two dozen 2 mm balls
  and said "there is no way I will ever get it installed." Use one-piece
  printed detents (Karambit).
- Overstressed printed spring arms take a set in PETG and wedge the halves
  apart. Design springs to sit fully relaxed in each click (Karambit).

## Print-in-place

**UNTESTED** unless a later note says otherwise.

- Swivel: 0.4 mm gaps (Carabiner).
- Chain links: ≥0.5 mm. The links could go no smaller than 5.2 mm wide
  (Charm).
- Hinges need to work free after printing (Mcon, Scouter).

## Flex

**Spool fins**

- **FAILED** — short spool fins at about 5–6% strain were "a bit stressed...
  not reusable."
- **PROVEN** — long spring leaves wrapped about 130° (5 leaves, 1.3 mm thick,
  about 0.26–0.55% strain) "worked perfectly."
- Keep strain under about 1% in ABS/PETG. Make each leaf 2–3 solid lines
  (Spool).

**Thin PETG (Carabiner)**

- **FAILED** — 3 mm thick "works but is so fragile."
- **FAILED** — after the circle version went to 3.0 mm, the clasp "snaps
  immediately."
- **FAILED** — a 1.35 mm gate wire "is going to SNAP."
- **PROVEN** that it was strong, and too thick for a 2 mm charm hole — thick
  v4 (5 mm thick, 5.25 mm wall).
- **PROVEN** — the reference carabiner's dimensions (4 mm wall, 3.2 mm thick,
  0.92 mm slit) bent into a 24.9 mm circle. He said "Perfect."

**TPU folding hinge**

- **PROVEN** — Keychain v10: tapered from 4 mm at the PETG down to 1.2 mm
  over the middle 11 mm of the bend.

## Hardware he has used

- **PROVEN** — keychain bolt M3×16 plus washers (Keychain).
- Countersunk M3×6 has been used. M2×25 has been used as a pin.
- Bearings: 6705ZZ (25×32×4), 6803-2RS (17×26×5), 608.
- Design around this hardware. The list of what he owns is in
  `jeff_workflow.md`.

## Croc folio, his stated sizes

These are his stated preferences (Croc), not a separate pass/fail print note.

- Panels vary organically between 1.4 and 1.8 mm. Foldable spine 0.6 mm.
- Elastic-cord holes 4 mm, with ≥4 mm of material to the edge.
- Snap button holes 2 mm, with flat zones of at least about 21 mm for a 15 mm
  snap head.
