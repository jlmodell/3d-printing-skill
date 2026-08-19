# Gridfinity — verified constants

Source of truth: `gridfinity-rebuilt-openscad/src/core/standard.scad` and the
gridfinity-unofficial specification. Every number below was re-measured on
generated meshes by cross-sectioning them, not copied on faith.

## Base profile

| Quantity | Value |
|---|---|
| Grid pitch | 42.0 mm |
| Bin outer footprint | `42*n - 0.5` mm (1×1 = 41.5) |
| Top corner radius | 3.75 mm |
| Base profile height | 4.95 mm |
| Base height incl. bridge | 7.0 mm |
| Height unit | 7.0 mm (a "6u" bin is 42 mm tall) |

Profile, bottom of foot upward, as (rise, outward run from narrowest):

    (0.00, 0.00)   45 deg chamfer starts, width 35.6
    (0.80, 0.80)   width 37.2
    (2.60, 0.80)   straight section ends, width 37.2
    (4.95, 2.95)   45 deg flare ends, width 41.5

So a correct part measures **35.60 / 37.20 / 37.20 / 41.50 mm** at
z = 0 / 0.8 / 2.6 / 4.95. `gridfinity_gen.py verify()` checks exactly this and
should be run on every generated part.

Cut the profile by inward offset from the 41.5 rounded rect: inset *d* gives
width `41.5 - 2d` and corner radius `3.75 - d`. At the bottom (d = 2.95) the
radius is 0.80 mm, which is why the corner never degenerates.

## Baseplates

A baseplate is a 4.95 mm slab with the foot profile subtracted at 42 mm pitch.
Material between cells is 0.5 mm at the top and 6.4 mm at the bottom, so every
socket wall slopes outward going up — **no overhangs, no supports, ever**.

When integrating a baseplate into a container floor, fill the cavity
edge-to-edge and centre the cell grid inside it. The leftover perimeter becomes
a flat ledge. This beats a floating island of exactly `n*42`: no crumb gutter
around the grid, more glue area, and the socket walls get side support.

Take the cavity outline from an actual cross-section of the container a couple
of mm above its floor (`mesh.section` → `polygons_full[0].interiors[0]`) rather
than assuming a rectangle — real containers have fillets and draft.

## Bins

Body above 4.95 mm is one solid of the full `42n-0.5` footprint; below it,
discrete feet per cell. The 0.5 mm gaps between feet bridge at z = 4.95, which
is standard and prints fine.

Cavity floor at z = 7.0 (base height). Wall 1.2 mm = 3 perimeters at 0.4 mm.

**Stacking lip:** the spec includes it *within* the nominal height, so a 6u bin
with a lip is still 42 mm overall. Omit it when bins live in a fixed-depth
drawer and cannot stack — the 4.4 mm it occupies is often exactly what decides
whether a full-depth bin fits. Say when you have omitted it.

**Magnet holes:** 6 × 2 mm, 2.4 mm deep pockets, 8 mm in from each corner.
Pointless unless the mating baseplate also has magnets — skip them by default
and tell the user why rather than silently adding unprintable pockets.

## Tiling a grid exactly

Cells available = `floor(W/42) × floor(D/42)`. Ask the user for the bin mix and
check it sums to the cell count before modelling anything; a mix that does not
tile means reprinting.

Worked example, 228.28 × 150.43 mm drawer floor → 5 × 3 = 15 cells:
2×3 (6) + 2×2 (4) + 2×1 ×2 (4) + 1×1 (1) = 15, tiles with no leftovers.

## Fit checks before delivering

- Bin height + baseplate seat vs. container clear height. The foot sinks
  4.95 mm into the socket, so usable height above the plate is
  `bin_height - 4.95`.
- Bin bounding boxes against the cavity outline, not just the cavity bbox.
- Pairwise bin overlap (neighbours should clear by ~0.5 mm, never touch).
- Check container walls at mid-height too: a rib or draft that misses the
  baseplate can still foul a tall bin.
