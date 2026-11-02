# Jeff's workflow

How to work with him, and where files go. Design rules are in
`jeff_design_rules.md`. Printers are in `jeff_printers.md`.

## Where files go

Designs and the print log live in
[grokalok-jmo-3d-designs](https://github.com/jlmodell/grokalok-jmo-3d-designs).

- Read and append `print-log.md` there (or a CSV if that is what the repo
  actually contains).
- Save each design at `designs/<project>/vN/`.
- Google Drive folder **3D Prints** is a backup copy, not the source of
  truth. Earlier jobs also used "3D Designs/\<project\>" (Maker),
  "3D Prints/\<project\>" (Karambit, SpeedStitch, Napkin), and
  "3D Print Charms."
- If a Drive download fails, attach the file in chat (Charm).
- The Drive connector can only trash or overwrite files it created. Files
  from his earlier assistant or account have to be deleted by him. Upload new
  versions alongside (Karambit, AirPod, Charm).
- If the designs repo cannot be cloned, use `seed/designs-repo/` in this
  skill, which is the same layout, and tell him the GitHub repo was not
  reachable. Do not keep two logs once the repo is reachable.

## One version folder

`designs/<project>/vN/` gets all of these:

- The mesh: STL, Bambu 3MF, or Orca-style 3MF, per `jeff_printers.md`.
- A short `README.md`: printer, material, settings, status.
- `NOTES.md`, from `templates/NOTES.md` in the designs repo: what changed,
  printer, material, slicer settings, fit results, what worked or failed,
  next steps.
- `images/`: renders, slicer screenshots, and photos of the real print.
  Embed those images in `NOTES.md`.

Always write `NOTES.md` when saving a design. Always save a preview image
into `images/` and embed it. When he sends a photo of the print, add it
under `images/` and embed it in `NOTES.md`. Do not wait for him to ask.

`designs/<project>/README.md` lists the versions and links each one, with a
thumbnail from that version's `images/`.

Images, STL, and 3MF are Git LFS in that repo (`.gitattributes`).

## Deleting old revisions

Delete old revisions only after he OKs a printed version, and only after he
confirms the exact list.

- Carabiner: 78 local files deleted after "Perfect" plus a yes.
- Oni: a mirrored STL was trashed after approval (Maker, Carabiner).

Until that yes, keep the old version and add the new one beside it. He asked
for a new folder per major version so files do not mix (SpeedStitch).

## Before building

Show a preview image before committing to the build. He has said "show me a
preview first," "Send me an image first," and "Let me know what you are
thinking by image before you commit" (Spool, Keychain, AirPod, Napkin). For a
mechanism, send a corner or a cross-section, not only a beauty shot.

## How to write to him

- Short and plain. On the oni back he said: "I'm not sure what you made. I
  just wanted a back to print and glue together."
- Explain a mechanism with an image ("show me with an image please") (Maker,
  Karambit).
- Tell him which parts to reprint and which to keep (Mcon, Karambit).
- He checks in often ("any luck?", "still going?"). Send a short progress
  note (Karambit, Mcon, Charm).
- Accuracy over confidence. Do not invent slicer setting names (Charm
  handoff). Do not invent print results. Keep **FAILED** and **UNTESTED**
  on anything that failed or was never confirmed.

## Hardware he owns

Design around this, not a catalog he did not buy.

- M3 screws and nuts in many lengths. Countersunk M3×6 has been used. M2
  screws. M2×25 used as a pin.
- Bearings: 6705ZZ (25×32×4), 6803-2RS (17×26×5), 608.
- Ruibapa 50-piece 304 stainless torsion spring kit.
- 15 mm button snaps, 2 mm G25 balls, D-rings.
- Hardened steel nozzles on all printers.

Sources: Karambit, SpeedStitch, AirPod, Keychain, Croc, Spool.

## Shopping, context only

He cancelled a Creality K3 pre-order and a Prusa order. He is watching the
Bambu H3C (9-tool, AMS 3H, TPU 75A at 2.85 mm, launch Nov 3, 2026) and the
P3C for charm work. He is hesitant about 2.85 mm TPU because he has a lot of
1.75 mm stock (Megathread). He does not own those machines. Do not design as
if he does.
