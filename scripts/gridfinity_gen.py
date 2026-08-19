#!/usr/bin/env python3
"""Gridfinity geometry generator -- spec-exact, no OpenSCAD, no external MCP.

Profile constants are the canonical spec (gridfinity-rebuilt standard.scad):
grid pitch 42.0, bin top 41.5, top corner radius 3.75, base profile height
4.95 in three steps -- 0.8 chamfer / 1.8 straight / 2.15 chamfer, total
horizontal run 2.95. Cross-sections of the output measure 35.60 / 37.20 /
41.50 mm exactly; verify() re-checks that on the generated mesh.

    # baseplate that fills a measured drawer cavity, sockets centered
    python gridfinity_gen.py baseplate --size 228.28x150.43 --out bp.stl

    # baseplate of an explicit cell count only (no surrounding ledge)
    python gridfinity_gen.py baseplate --cells 5x3 --out bp.stl

    # bins (height in 7 mm units; 15u = 105 mm)
    python gridfinity_gen.py bin --cells 2x3 --units 15 --out bin_2x3.stl

    # how many cells fit, and what tiles the result exactly
    python gridfinity_gen.py fit --size 228.28x150.43
"""
import argparse
import sys

import numpy as np
import trimesh
from shapely.geometry import Polygon

PITCH = 42.0
TOP = 41.5
RTOP = 3.75
PROFILE_H = 4.95
BASE_H = 7.0          # profile + bridge; bin cavity floor sits here
# (height above profile bottom, inward inset from TOP)
PROFILE = [(0.0, 2.95), (0.8, 2.15), (2.6, 2.15), (4.95, 0.0)]


def rrect(w, h, r, n=16):
    """Rounded rectangle as an ordered point ring. Constant point count for a
    given n, so rings at different insets loft with 1:1 correspondence."""
    pts = []
    for cx, cy, a0 in [(w / 2 - r, h / 2 - r, 0), (-(w / 2 - r), h / 2 - r, 90),
                       (-(w / 2 - r), -(h / 2 - r), 180), (w / 2 - r, -(h / 2 - r), 270)]:
        for k in range(n + 1):
            a = np.radians(a0 + 90 * k / n)
            pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return np.array(pts)


def _loft(rings):
    N = len(rings[0])
    V = np.vstack(rings)
    F = []
    for k in range(len(rings) - 1):
        a, b = k * N, (k + 1) * N
        for i in range(N):
            j = (i + 1) % N
            F += [[a + i, b + i, b + j], [a + i, b + j, a + j]]
    for k, flip in [(0, True), (len(rings) - 1, False)]:
        base = k * N
        c = len(V)
        V = np.vstack([V, rings[k].mean(0)])
        for i in range(N):
            j = (i + 1) % N
            F.append([c, base + j, base + i] if flip else [c, base + i, base + j])
    m = trimesh.Trimesh(vertices=V, faces=np.array(F), process=True)
    m.fix_normals()          # loft winding is inconsistent; manifold3d rejects it otherwise
    return m


def socket(cx=0.0, cy=0.0, z0=0.0, over=0.6, under=0.10, n=16):
    """The bin-foot solid. Subtract it from a slab to get a baseplate socket."""
    # Only add the over/under extension rings when they are non-zero -- a
    # zero-length extension duplicates a ring at the same z and the degenerate
    # band makes manifold3d reject the solid ("Not all meshes are volumes").
    prof = ([(-under, 2.95)] if under > 0 else []) + PROFILE + \
           ([(PROFILE_H + over, 0.0)] if over > 0 else [])
    rings = []
    for z, d in prof:
        p = rrect(TOP - 2 * d, TOP - 2 * d, RTOP - d, n)
        rings.append(np.column_stack([p[:, 0] + cx, p[:, 1] + cy,
                                      np.full(len(p), z + z0)]))
    return _loft(rings)


def cells_that_fit(w, d):
    return int(w // PITCH), int(d // PITCH)


def baseplate(width=None, depth=None, nx=None, ny=None, outline=None):
    """Slab of PROFILE_H with nx*ny sockets cut through, centered.

    width/depth: fill this footprint edge-to-edge (leftover becomes a flat
    ledge -- no crumb gutter, and stronger than a floating island).
    outline: optional shapely Polygon to use verbatim instead of a rectangle,
    e.g. the exact cavity ring from a drawer cross-section.
    """
    if outline is not None:
        minx, miny, maxx, maxy = outline.bounds
        poly = outline
        width, depth = maxx - minx, maxy - miny
        cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    else:
        if width is None:
            width, depth = nx * PITCH, ny * PITCH
        poly = Polygon([(-width / 2, -depth / 2), (width / 2, -depth / 2),
                        (width / 2, depth / 2), (-width / 2, depth / 2)])
        cx = cy = 0.0
    if nx is None:
        nx, ny = cells_that_fit(width, depth)
    if nx < 1 or ny < 1:
        raise SystemExit(f"footprint {width:.2f}x{depth:.2f} fits no 42 mm cell")

    slab = trimesh.creation.extrude_polygon(poly, PROFILE_H)
    socks = [socket(cx + (i - (nx - 1) / 2) * PITCH, cy + (j - (ny - 1) / 2) * PITCH)
             for i in range(nx) for j in range(ny)]
    out = trimesh.boolean.difference([slab, trimesh.boolean.union(socks)])
    out.merge_vertices()
    out.update_faces(out.nondegenerate_faces())
    out.remove_unreferenced_vertices()
    return out, nx, ny


def bin_(nx, ny, units=6, wall=1.2):
    """Gridfinity bin, nx*ny cells, height units*7 mm.

    No stacking lip. The lip only matters if bins stack; in a fixed-depth
    drawer they can't, and the lip's extra 4.4 mm is often exactly what makes
    a full-depth bin not fit. Add one deliberately if the user asks.
    """
    H = 7.0 * units
    feet = [socket((i - (nx - 1) / 2) * PITCH, (j - (ny - 1) / 2) * PITCH, over=0.0, under=0.0)
            for i in range(nx) for j in range(ny)]
    body_poly = Polygon(rrect(nx * PITCH - 0.5, ny * PITCH - 0.5, RTOP, 24))
    body = trimesh.creation.extrude_polygon(body_poly, H - PROFILE_H)
    body.apply_translation([0, 0, PROFILE_H])
    cav_poly = Polygon(rrect(nx * PITCH - 0.5 - 2 * wall, ny * PITCH - 0.5 - 2 * wall,
                             max(RTOP - wall, 0.2), 24))
    cav = trimesh.creation.extrude_polygon(cav_poly, H - BASE_H + 2)
    cav.apply_translation([0, 0, BASE_H])
    out = trimesh.boolean.difference([trimesh.boolean.union(feet + [body]), cav])
    out.merge_vertices()
    out.update_faces(out.nondegenerate_faces())
    out.remove_unreferenced_vertices()
    return out


def verify(mesh, kind, z0=0.0):
    """Re-measure the spec profile on the produced mesh. Never skip this."""
    checks = [(z0 + 0.001, 35.60), (z0 + 0.8, 37.20), (z0 + 2.6, 37.20), (z0 + 4.949, 41.50)]
    print(f"  watertight={mesh.is_watertight} bodies={mesh.body_count} "
          f"ext={np.round(mesh.extents, 2)} vol={mesh.volume/1000:.1f}cm3")
    ok = mesh.is_watertight
    for z, want in checks:
        sec = mesh.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec is None:
            continue
        p, _ = sec.to_planar(to_2D=np.eye(4))
        sizes = []
        for pg in p.polygons_full:
            rings = pg.interiors if kind == "baseplate" else [pg.exterior]
            for r in rings:
                c = np.array(r.coords)
                sizes.append(c[:, 0].max() - c[:, 0].min())
        if sizes:
            got = float(np.median(sizes))
            good = abs(got - want) < 0.12
            ok &= good
            print(f"  z+{z-z0:5.3f}: {got:7.3f} mm (spec {want})  {'ok' if good else 'OUT OF SPEC'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("baseplate")
    b.add_argument("--size", help="WxD mm footprint to fill edge-to-edge")
    b.add_argument("--cells", help="NXxNY explicit cell count")
    b.add_argument("--out", required=True)
    n = sub.add_parser("bin")
    n.add_argument("--cells", required=True)
    n.add_argument("--units", type=int, default=6)
    n.add_argument("--wall", type=float, default=1.2)
    n.add_argument("--out", required=True)
    f = sub.add_parser("fit")
    f.add_argument("--size", required=True)
    a = ap.parse_args()

    if a.cmd == "fit":
        w, d = [float(x) for x in a.size.lower().split("x")]
        nx, ny = cells_that_fit(w, d)
        print(f"footprint {w} x {d} mm -> {nx} x {ny} cells ({nx*ny} total)")
        print(f"grid {nx*PITCH:.1f} x {ny*PITCH:.1f} mm, "
              f"margin {(w-nx*PITCH)/2:.2f} mm each side / {(d-ny*PITCH)/2:.2f} mm front-back")
        return 0

    if a.cmd == "baseplate":
        nx = ny = None
        w = d = None
        if a.cells:
            nx, ny = [int(x) for x in a.cells.lower().split("x")]
        if a.size:
            w, d = [float(x) for x in a.size.lower().split("x")]
        m, nx, ny = baseplate(width=w, depth=d, nx=nx, ny=ny)
        print(f"baseplate {nx}x{ny}")
        ok = verify(m, "baseplate")
    else:
        nx, ny = [int(x) for x in a.cells.lower().split("x")]
        m = bin_(nx, ny, a.units, a.wall)
        print(f"bin {nx}x{ny} {a.units}u ({a.units*7} mm)")
        ok = verify(m, "bin")

    m.export(a.out)
    print(f"  wrote {a.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
