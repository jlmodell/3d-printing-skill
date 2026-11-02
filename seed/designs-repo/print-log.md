# Print log

Starter log from Jeff's project transcripts, read Nov 2, 2026. Eighteen
entries. Printer is **unknown** when the transcript did not name one. Do not
fill that in later unless he says so.

Labels:

- **PROVEN** — he printed it and said it worked.
- **FAILED** — he printed it and it failed.
- **UNTESTED** — designed or advised, no print result in the transcript.

Append new entries below, numbered, with the same fields. `success`,
`partial`, and `fail` are the result values. A label can be stricter than the
result: a partial print can still contain a **FAILED** mechanism and a
**PROVEN** later fix. Say which is which.

| # | Model | Printer | Material | Result |
|---|---|---|---|---|
| 1 | Karambit 6705 v11 | Snapmaker U1 | PETG 245/70 | success |
| 2 | Karambit v10 nut pockets | Snapmaker U1 | PETG | fail |
| 3 | Karambit slider coupon | Snapmaker U1 | PETG | success |
| 4 | Karambit PLA support interface | Snapmaker U1 | PETG+PLA | partial |
| 5 | Keychain v7 | Snapmaker U1 | PETG+TPU | fail |
| 6 | Keychain v10 | Snapmaker U1 | PETG+TPU | success |
| 7 | Backplate pause insert | Snapmaker U1 | PETG on TPU | fail |
| 8 | AirPod holder v9 → v10 | unknown | PETG | fail → success |
| 9 | Mcon insert v3 / adapter v4 | unknown | PETG | fail |
| 10 | Spool fins (short) | unknown | ABS | partial |
| 11 | Carabiner circle (reference dimensions) | unknown | PETG | success |
| 12 | Charm cup | Snapmaker U1 | TPU 95A + PLA | success |
| 13 | Charm Doom (silk gold) | Snapmaker U1 | TPU + silk PLA | partial |
| 14 | Charm face-down seigaiha | Snapmaker U1 | TPU + PLA | partial |
| 15 | TPU 57D charm | Snapmaker U1 | TPU 57D + PLA | fail |
| 16 | Kobra flexi (from-scratch joints) | Kobra X | PETG | fail |
| 17 | Oni back | unknown | PETG | success |
| 18 | Kobra 0.25 job | Kobra X | PETG | fail |

## 1. Karambit 6705 v11

- Printer: Snapmaker U1
- Material: PETG 245/70
- Result: success
- Label: **PROVEN** (v11). v11.1 chamfer restore is **UNTESTED**.
- Source: Karambit
- Issue → fix: v10 detent engagement was 0.17 mm into the notch while the slider had 0.22 mm of side play, so it never clicked. v11 used a stiffer 1.5 mm tab, backed up so the slider cannot drift, plus deeper notches. Supports fully off.
- Notes: He said v11 "printed the best of all versions." v11 lost the chamfers. v11.1 put them back (1 mm outer, 1 mm thumb slot, 0.5 mm finger ring). No print result was recorded for v11.1.

## 2. Karambit v10 nut pockets

- Printer: Snapmaker U1
- Material: PETG
- Result: fail
- Label: **FAILED**
- Source: Karambit
- Issue → fix: Chamfered nut pockets filled with support and fused. Use straight hex walls, a one-layer stepped bridge ceiling, and no chamfer. Supports fully off, not "build plate only."

## 3. Karambit slider coupon

- Printer: Snapmaker U1
- Material: PETG
- Result: success
- Label: **PROVEN**
- Source: Karambit
- Issue → fix: Lanes at 0.15 / 0.20 / 0.25 / 0.30 mm. He said 0.20 and 0.25 were both good. The knife channel used 0.22 mm.

## 4. Karambit PLA support interface

- Printer: Snapmaker U1
- Material: PETG+PLA
- Result: partial
- Label: **FAILED** for the PLA interface. The HIPS profile import is **UNTESTED**.
- Source: Karambit
- Issue → fix: PLA support interface on PETG at 0 top-Z gap "didn't come off easily at all." Switched to HIPS. Advised HIPS settings: 235–240 °C, fan 30–50%, support interface only (2–3 layers), bed stays 70. A "Generic HIPS @U1" profile was made from Generic ABS. That import was not tested.

## 5. Keychain v7

- Printer: Snapmaker U1
- Material: PETG+TPU
- Result: fail
- Label: **FAILED**
- Source: Keychain
- Issue → fix: TPU curled at the interlock, got snagged, and oozed during tool changes (spaghetti). Later v10 put TPU on layer 1 with PETG, buried a dovetail plus 4 PETG pins, ran TPU at about 20 mm/s, and used a prime tower. Also: no raised boss on the bed side, a brim, Z-hop on, dry the TPU.

## 6. Keychain v10

- Printer: Snapmaker U1
- Material: PETG+TPU
- Result: success
- Label: **PROVEN**
- Source: Keychain
- Issue → fix: PETG and TPU side by side from layer 1, buried dovetail, PETG pins. "Worked perfectly." Bolt is M3×16 plus washers. Hinge tapers from 4 mm at the PETG to 1.2 mm over the middle 11 mm.

## 7. Backplate pause insert

- Printer: Snapmaker U1
- Material: PETG on TPU
- Result: fail
- Label: **FAILED**
- Source: Backplate
- Issue → fix: PETG printed onto TPU beaded into "pills of PETG" and would not bond. Switched to a glued two-piece. The one-plate layout needs about 198 mm, so it fits the A1 and not the A1 mini.

## 8. AirPod holder v9 → v10

- Printer: unknown
- Material: PETG
- Result: fail → success
- Label: v9 **FAILED**. v10 **PROVEN**. The v11 ease to 0.2 mm per side is **UNTESTED** (no print result recorded).
- Source: AirPod
- Issue → fix: A 0.55 mm catch "never caught with any strength — fell out with any movement." v10 uses 6 catches (4 inner hooks at 1.8 mm plus 2 outer latches) and "fit perfectly together." Fingers at 0.3 mm per side interference "fit perfectly." He asked to ease off a tad, so v11 went to 0.2 mm per side.
- Notes: The v9 handoff said work-prototype parts are translucent PETG or PCTG. This entry's material is the PETG the starter table recorded.

## 9. Mcon insert v3 / adapter v4

- Printer: unknown
- Material: PETG
- Result: fail
- Label: **FAILED** for the tight rail. The shortened sliding shelf is a separate **PROVEN** seat (photo). v6 J-hook is **UNTESTED**.
- Source: Mcon
- Issue → fix: 0.18 mm clearance over a 40 mm rail jammed. A tight rail bulged a 1.2 mm roof over the slot. Use about 0.25–0.30 mm clearance, widen the slot 0.15 mm per side, and keep the roof ≥1.5 mm (plate 3.75 mm). Detent bumps only on the last 2.5 mm. Elephant's foot compensation ≤0.1 mm.
- Notes: The rail was cut to 16.5 mm because the controller key blocks the slot about 17 mm in. Shelf v3 seated and caught the phone, and needed more reach.

## 10. Spool fins (short)

- Printer: unknown
- Material: ABS
- Result: partial
- Label: short fins **FAILED** (he called them not reusable). Long spring leaves **PROVEN**.
- Source: Spool
- Issue → fix: Short fins at about 5–6% strain were "a bit stressed... not reusable." Long spring leaves wrapped about 130° (5 leaves, 1.3 mm thick, about 0.26–0.55% strain) "worked perfectly." Keep strain under about 1% in ABS/PETG. Each leaf 2–3 solid lines.

## 11. Carabiner circle (reference dimensions)

- Printer: unknown
- Material: PETG
- Result: success
- Label: reference geometry **PROVEN**. The thin versions **FAILED**.
- Source: Carabiner
- Issue → fix: 3 mm thickness was fragile. At 3.0 mm the clasp "snaps immediately." A 1.35 mm gate wire "is going to SNAP." Gate cuts at 0.35 mm fused. 0.55–0.6 mm is OK. Thick v4 (5 mm thick, 5.25 mm wall) was strong and too thick for a 2 mm charm hole. The reference dimensions (4 mm wall, 3.2 mm thick, 0.92 mm slit) bent into a 24.9 mm circle. He said "Perfect."

## 12. Charm cup

- Printer: Snapmaker U1
- Material: TPU 95A + PLA
- Result: success
- Label: **PROVEN**
- Source: Charm
- Issue → fix: PLA art on a TPU 95A orange base "came out awesome."

## 13. Charm Doom (silk gold)

- Printer: Snapmaker U1
- Material: TPU + silk PLA
- Result: partial
- Label: **FAILED** for the small gold islands. v4's no-gold mask has no recorded print result (**UNTESTED**).
- Source: Charm
- Issue → fix: Small silk-gold pieces fell off TPU. Drop tiny islands. Use chunky regions (islands ≥4 mm²). Dr Doom v4 used one big silver mask, no gold, and a 71 mm² minimum piece.

## 14. Charm face-down seigaiha

- Printer: Snapmaker U1
- Material: TPU + PLA
- Result: partial
- Label: face-down **FAILED** as the look he wanted. Face-up is the tested orientation for stitched charms.
- Source: Charm
- Issue → fix: Face-down (TPU on top, art flush on the bed side) was "not as nice as the normal print" and "very thick." Use face-down only for thick charms without stitch holes. Default stitched charms to face-up when using the Charm-bot spec.

## 15. TPU 57D charm

- Printer: Snapmaker U1
- Material: TPU 57D + PLA
- Result: fail
- Label: **FAILED**
- Source: Charm
- Issue → fix: Pilly surface, and PLA barely stuck. The TPU may have been wet. Profile built from Snapmaker "Generic TPU 95A HF @U1": 235 °C, fan 100%, textured PEI at 45 °C, max volumetric speed 8 mm³/s. Dry TPU at 70 °C for 6 h was advised. He leaned toward 95A yellow instead. Drying was not recorded as a confirmed reprint fix.

## 16. Kobra flexi (from-scratch joints)

- Printer: Anycubic Kobra X
- Material: PETG
- Result: fail
- Label: from-scratch fork-push legs **FAILED**. Reusing his body and hinges **PROVEN**.
- Source: KobraFiles
- Issue → fix: Legs designed from scratch fell off. Reuse his working body and hinges and only swap heads. A plate of 9 of those took 4 h. A single took 2 h.

## 17. Oni back

- Printer: unknown
- Material: PETG
- Result: success
- Label: **PROVEN**
- Source: Maker
- Issue → fix: Glue-on 2.2 mm back (1.6 mm plate + 0.6 mm seigaiha), 0.12 mm layers, CA or epoxy. "Came out great."
- Notes: The project file carried someone else's P1S profile. That does not mean the printer was a P1S. He was told to switch the printer and press Arrange.

## 18. Kobra 0.25 job

- Printer: Anycubic Kobra X
- Material: PETG
- Result: fail
- Label: **FAILED** to send. The re-slice steps were the diagnosis. No successful reprint was recorded.
- Source: Kobra.25
- Issue → fix: The job would not send because the nozzle size did not match. Set the nozzle to 0.25 on the touchscreen, choose the 0.25 preset in Anycubic Slicer Next, and re-slice.
- Notes: Guidance given with that job, not a confirmed good print: PETG at 2–4 mm³/s, 0.08–0.15 mm layers, 0.25–0.30 mm line width, outer walls around 30 mm/s, Arachne walls on, filament dried.
