# grokalok-jmo-3d-designs

Jeff's 3D designs and print log. This tree is the seed for
[github.com/jlmodell/grokalok-jmo-3d-designs](https://github.com/jlmodell/grokalok-jmo-3d-designs).
That repo was not reachable when this seed was written (Nov 2, 2026), so the
files live under `seed/designs-repo/` in the 3d-printing skill until they can
be pushed to their own `main`.

Google Drive **3D Prints** is a backup copy. This repo is the one to read and
append.

## Layout

```text
print-log.md
templates/NOTES.md
templates/version-README.md
templates/project-README.md
designs/<project>/README.md          # links versions, with a thumbnail
designs/<project>/vN/README.md        # printer, material, settings, status
designs/<project>/vN/NOTES.md         # what changed, fits, results, next steps
designs/<project>/vN/images/          # preview, slicer shots, print photos
designs/<project>/vN/*.(stl|3mf)
```

No project folders are created yet. The starter history is in `print-log.md`.
Add `designs/<project>/vN/` when there is a mesh to save, not before.

## What goes in a version

- The file the printer needs: Bambu 3MF (A1, A1 mini, X1 Carbon), Orca-style
  3MF with filament slots (Snapmaker U1), or STL (Anycubic Kobra X).
- `README.md` from `templates/version-README.md`.
- `NOTES.md` from `templates/NOTES.md`. Embed every image in `images/`.
- A preview render at save time. Add Jeff's print photos when he sends them.
- The project `README.md` links the version and shows a thumbnail.

Images, STL, and 3MF are Git LFS (`.gitattributes`). Run `git lfs install`
before adding any of those files.

## Print log

`print-log.md` has 18 entries from transcripts read Nov 2, 2026. Append a new
entry after a real result. Do not invent a printer when the entry says
unknown, and do not relabel **FAILED** or **UNTESTED** without a print he
confirmed.

Delete an old version only after he OKs a print and confirms the exact list.
