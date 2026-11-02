# Jeff's design rules

Labels: **PROVEN**, **FAILED**, **UNTESTED**. Charm hole, groove, and pocket
numbers are in `jeff_charms.md`, not here.

## Seigaiha

His favorite motif is Great Wave seigaiha. He wants it on almost everything
(Maker).

- **Two-color:** a flush cream inlay on navy (Karambit).
- **One color:** waves cut or debossed into the outer face. A one-color handle
  without waves "feels lacking."
  - Cut through the outer skin only, about 1–1.2 mm deep, never through to
    internal cavities.
  - Keep the bed side flat.
  - Keychain: "I don't want multicolor waves, just cut outs."
- **Wave size:** bigger, bolder scales on large faces (the backplate went to
  28 mm across). 0.75 in (19 mm) scales on a 2×4 in charm (Backplate, Charm).
- **MagSafe:** keep relief under 0.4 mm so MagSafe still works (Backplate).

## Chamfers

He asks for this repeatedly ("Make sure to chamfer everything"; "you lost all
the chamfers now"). Sources: Keychain, Charm, Karambit.

- Outer edges: 1.0–1.2 mm at 45°. Karambit used 1.0. Keychain used 1.2
  maximum on 4 mm scales.
- Bed-side edges: 0.3–0.5 mm, to limit elephant's foot.
- **Never chamfer nut pockets.** The slicer put support inside them and it
  fused. Use straight hex walls with a one-layer stepped bridge ceiling.
  Turn supports **fully off**, not "build plate only" (Karambit). **FAILED**
  when the pockets were chamfered.
- Kids' items: rounded edges, no sharp points. 3 mm corner radius on the
  bookmarks. The witch's hat ends in a ball (KobraFiles).
- Small fillets, about 0.5 mm, where lugs meet a plate add strength (Mcon).

## Strength and orientation

- Print flexing features **flat**, so the extrusion lines run along the flex.
  A slider nub printed vertically sheared off at a layer line (Karambit).
- Gates should spring **in the print plane**, not across the layers
  (Carabiner).
- End slits in round holes so cracks do not start there (Carabiner).
- Overhangs he has used: ≤45°. Replace flat overhangs with 45° wedges or
  tapers. The cam-buckle roller ends were tapered at 45° (AirPod,
  KobraFiles).
- Minimum feature 0.6 mm, and ≤45° overhang, for general prints (KobraFiles).

## Multi-material that worked (Keychain)

**PROVEN** — v10, PETG + TPU:

- Layer 1 is PETG and TPU together on the bed.
- The TPU tongue is buried in the scale with a dovetail and 4 PETG pins.
- The TPU stops 1.2 mm (6 layers) below the top face, so the outside is solid
  PETG.
- No floating TPU over a support pad. The v8/v9 TPU-off-the-plate approaches
  were dropped.

**FAILED** — v7 spaghetti. The TPU curled at the interlock, got snagged, and
oozed during tool changes. What changed after that:

- No raised boss on the bed side.
- TPU at about 20 mm/s, with a prime tower and a brim.
- Z-hop on.
- Dry the TPU.

PETG printed on top of TPU is a separate failure (pills, no bond). See
`jeff_materials.md`. Do not stack PETG onto TPU and expect it to stick.

## Reference first

When he sends a reference, build on it. Do not start over.

- **FAILED** — scouter rev1 from scratch was "not really any amount close to
  what I was thinking" (Scouter).
- **FAILED** — flexi legs from scratch with fork-push joints fell off.
  **PROVEN** — reusing his working body and hinges, and only swapping heads,
  worked. A plate of 9 took 4 h (KobraFiles).
- **PROVEN** — the carabiner final used the reference dimensions and became a
  circle. He said "Perfect" (Carabiner).
- Logos and crests: trace a flat-vector reference. A hand-drawn eagle read as
  "quetzalcoatl" (KobraFiles).
- Charm loops must be fused solidly into the head with a ≥4.8 mm neck. A loop
  that only touches the tip floats or breaks off (KobraFiles).

## Keep it simple

He has said "back to basics" on Napkin, Carabiner, and Karambit.

- Over-engineered clip systems (gutters, downspouts, two-piece L pegs) were
  rejected for a one-piece U clamp with plain pop-in pegs and relief slits
  (Napkin). No print result yet on that clamp.
- An extra connector part was rejected ("nope nope") (Carabiner).
- A long cradle "looks so long," and he did not understand it (Mcon).

## Objects in the file

Every printable piece is a separate named object. He has asked for 3MFs with
each piece separate (Karambit). Color parts get names. See `jeff_printers.md`
for which container each machine actually gets.
