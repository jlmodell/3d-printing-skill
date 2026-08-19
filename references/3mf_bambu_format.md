# 3MF format and Bambu Studio project files

## Two kinds of 3MF

1. **Plain 3MF** — just geometry (+ optional materials). What trimesh exports.
   Opens fine in Bambu Studio as an imported model.
2. **Bambu Studio project 3MF** — geometry PLUS `Metadata/` payload: print
   settings, plate layout, filament mappings, paint data, modifiers. Treat
   these as precious: round-tripping through trimesh **strips all of it**.

## Container layout (a 3MF is a zip)

```
[Content_Types].xml
_rels/.rels
3D/3dmodel.model            ← core geometry XML (always)
3D/Objects/object_N.model   ← Bambu sometimes splits objects here
Metadata/model_settings.config   ← per-object/part settings, plate assignment
Metadata/project_settings.config ← full printer/filament/process profiles
Metadata/slice_info.config, plate_N.png, ...
```

Core XML namespace: `http://schemas.microsoft.com/3dmanufacturing/core/2015/02`.
Units: `<model unit="millimeter">` (Bambu always uses mm).

Geometry lives in `<resources><object id="N"><mesh><vertices>/<triangles>`.
`<build><item objectid="N" transform="..."/>` places objects on the plate
(transform = row-major 4×3 affine, 12 numbers).

## Bambu paint data

Painted models store per-triangle attributes on `<triangle>` elements:
`paint_color="..."` and/or `slic3rpe:mmu_segmentation="..."` (encoded strings).
They are **positional** — valid only while the triangle list is unchanged.

Consequences:
- Uniform scale / move / rotate via in-place vertex editing (bambu_3mf.py
  `transform`) → paint survives.
- Booleans, remeshing, smart_scale recut mode, trimesh round-trip → paint lost.
  Warn the user before doing this to a painted file, and offer `--mode project`
  scaling instead.

## Editing rules that keep Bambu Studio happy

- Preserve every zip entry you don't intentionally change, byte-for-byte
  (bambu_3mf.py `rewrite_3mf` does this). Don't re-serialize XML you didn't touch.
- Keep object `id`s stable; `Metadata/model_settings.config` references them.
- Adding geometry to a project file is a **solved problem** — use
  `scripts/project_3mf.py`, not a trimesh round-trip and not a boolean. It
  rewrites only the four entries that must change and copies every other zip
  entry byte-for-byte, so paint on untouched objects survives. Validated on a
  6-plate H2C project: 141/491/792/1228/2234/2661 painted triangles all intact
  after adding both a part and a plate. Falling back to "deliver plain geometry
  and let the user re-apply settings" throws away their printer profile for no
  reason.
- To add a body to an **existing** object, add it as a second `<part>` rather
  than booleaning it in. The slicer fuses parts of one object, so the printed
  result is identical, but the original triangle list — and its paint — is
  never touched. Four edits: new `3D/Objects/object_N.model`, a `<component>`
  in that object, a `<Relationship>`, and a `<part>` in model_settings.
- **Object-local vs print scale.** Meshes are stored unscaled; the `<build>`
  `<item transform>` carries the scale (e.g. 1.6494). A part you modelled at
  print size must be divided by that scale before embedding, or it lands wrong
  by exactly that factor. `add-part --print-scale` does this.
- Transform decoding, verified: the 12 numbers are column-major 3×4 —
  `[[t0,t3,t6,t9],[t1,t4,t7,t10],[t2,t5,t8,t11],[0,0,0,1]]`.

## Plate grid

Bambu lays plates on one infinite sheet, 3 per row, striding **bed size × 1.2**.
For a 330 × 320 bed that is 396 × 384 mm — confirmed against all six plates of a
real project. Plate index `p` (0-based) sits at
`col = p % 3, row = p // 3`, global offset `(col*396, -row*384)`.
An object's bed-local position is its item translation minus that offset.

Get the bed from `printable_area` in `Metadata/project_settings.config`; do not
hardcode it. If a new plate's objects land off-bed the user can press A to
re-arrange, but getting it right means the file opens ready to slice.
- Colors for new plain 3MFs: `<basematerials id="M"><base name displaycolor="#RRGGBBAA">`,
  then `pid="M" pindex="i"` on the object. Bambu Studio maps distinct colors
  to filament slots on import — ideal for the user's multi-color H2C prints.
- Per-triangle color regions in a plain 3MF are unreliable across slicers; for
  multi-color parts prefer one object per color region.

## Checks after writing a 3MF

- `python scripts/bambu_3mf.py inspect out.3mf` — objects present, painted flag correct.
- `python scripts/mesh_info.py out.3mf` — dimensions & watertightness.
- Unzip and diff entry lists against the input when you meant to preserve metadata.
