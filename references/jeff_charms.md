# Charms

Two specs. Use the studio spec unless he asks for the tested one. Do not
blend the numbers.

Labels: **PROVEN**, **FAILED**, **UNTESTED**.

## Default — studio spec

This is the current default. It comes from the latest studio spec he asked
the skill to use. It is **not** a print result from the Charm bot, and it
does not match the Charm bot's tested numbers. No print of these exact
figures was in the transcripts.

- Stitch holes **2.4 mm**. Shape was not stated. Do not assume oval or round.
- Groove **0.6 mm**. Width was not stated.
- Art sunk **0.8 mm** into pockets.
- Slicer interlocking **2–3 layers**.
- Body **TPU**, art **PLA**.

The studio list does not state print orientation. Do not assume face-down.
The parent brief also mentioned flush inlays on the bed side among the
Grokalok-session values. That phrase is not part of the default above.

A parent summary described a Game Boy charm: a 2×2 in cartridge on a TPU
base with 3 PLA colours on the U1 (T1 TPU, T2–T4 PLA), rounded stitch holes
plus a groove. That summary was outside the bots that were read. **UNTESTED.**

## Proven alternative — Charm bot

Tested on the Charm bot. Use this set together when he wants the printed
spec, not a mix with the studio numbers.

- Stitch holes **round, 1.7 mm** (the same size as the corner circles). He
  said round holes were fine because it is not as critical as leather
  stitching.
- Groove **1.2 mm wide × 0.6 mm deep**, through the stitch holes, leaving
  1.4 mm of base under it.
- Art sunk **0.6 mm** into the base. v2 did this after PETG-on-TPU-GF bonding
  trouble. The material pair that then printed well was PLA on TPU 95A, not
  PETG on TPU.
- **Face-up** for stitched charms. Face-down (TPU on top, art flush on the bed
  side) was "not as nice as the normal print" and "very thick." Face-down
  only for thick charms without stitch holes.

**PROVEN** — coffee cup charm, PLA on a TPU 95A orange base, U1: "came out
awesome."

## Other Charm-bot rules

These sat with the tested spec. They are not in the studio default list.

- Islands ≥4 mm². Features ≥0.9 mm.
- Chunky colour regions. **FAILED** — small silk-gold PLA bits on TPU fell
  off. Dr Doom v4 went to one big silver mask, no gold, and a 71 mm² minimum
  piece. A print result for v4 itself was not recorded.
- Spider-Man white-sticker outline: he called them "fire." The dark red
  outline got lost on the red base.
- Every design grew 0.05 in so the groove clears the border. Sizes:
  1.55 / 1.8 / 2.05 / 3.05 in.
- Stitch holes started as 2.0×1.0 mm ovals slanted ±25° (mirrored
  front/back), 3.0–3.2 mm in from the edge. He then moved to the 1.7 mm
  rounds above.
- Corner holes 1.7 mm. Paracord hole 5 mm in a 10 mm loop.
- 2 in reads noticeably better than 1.75 in for detailed art. Pixel art at
  1.55 in is about 1 mm pixels, which is at the limit. He said "go straight
  to 2." Letters about 5 mm tall are readable. 3–3.6 mm is risky.
- Hook-and-loop patch variant: no groove, no loop, flat back. TPU can be hard
  to glue, so sew-on Velcro was advised.
- Chain links ≥0.5 mm, and no smaller than 5.2 mm wide.
- Wave size on a 2×4 in charm: 0.75 in (19 mm) scales. See
  `jeff_design_rules.md`.

## Materials on a charm

- Default pair is TPU body and PLA art (studio).
- **PROVEN** pair already printed: PLA on TPU 95A (cup).
- **FAILED:** PETG printed onto TPU (pills). Silk-gold specks on TPU. PLA on
  TPU 57D. Details in `jeff_materials.md`.
- TPU-GF (black) was the original patch base.
- U1 is the multi-material machine. TPU does not go through a Bambu AMS.

## Bookmarks (KobraFiles)

45×150 mm.

- Gryffindor and Slytherin: 2.6 mm (2.0 base + 0.6 colour).
- Ravenclaw: 2.0 mm. Clip tongue widened from 14 to 16 mm and shortened from
  30 to 27 mm.

Halloween flexis were built on his body, not from scratch. A plate of 9 took
4 h.
