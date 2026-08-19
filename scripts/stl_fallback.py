#!/usr/bin/env python3
"""Zero-dependency (numpy + stdlib) STL/3MF fallback for restricted sandboxes.

Use when trimesh/manifold3d can't be installed. Supports:
  info      — dimensions/triangle count of a binary or ASCII STL
  scale     — uniform scale with optional protected cylinders (radial
              projection of hole-wall vertices back to original radius —
              same as smart_scale.py --mode project)
  to3mf     — wrap an STL into a minimal plain 3MF (mm units, optional color)

Usage:
  python stl_fallback.py info model.stl
  python stl_fallback.py scale in.stl out.stl --scale 1.5 \
      --protect "cyl:cx,cy,cz,ax,ay,az,d,depth,blind" ...
  python stl_fallback.py to3mf in.stl out.3mf [--color "#00CC66"]

Protected-feature strings use the same format as smart_scale.py. Feature
positions must be measured/known (e.g. from a previous detect_features.py run
or from the model's design); this fallback does not auto-detect.
"""
import argparse
import json
import struct
import sys
import zipfile

import numpy as np


def read_stl(path):
    with open(path, "rb") as f:
        head = f.read(5)
    if head == b"solid":
        # could still be binary; try ASCII parse, fall back
        try:
            return read_stl_ascii(path)
        except Exception:
            pass
    return read_stl_binary(path)


def read_stl_binary(path):
    with open(path, "rb") as f:
        f.seek(80)
        n = struct.unpack("<I", f.read(4))[0]
        data = np.frombuffer(f.read(n * 50), dtype=np.uint8).reshape(n, 50)
    tri = data[:, 12:48].copy().view("<f4").reshape(n, 3, 3).astype(np.float64)
    return tri


def read_stl_ascii(path):
    verts = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("vertex"):
                verts.append([float(x) for x in line.split()[1:4]])
    tri = np.array(verts, dtype=np.float64)
    if len(tri) % 3:
        raise ValueError("bad ascii stl")
    return tri.reshape(-1, 3, 3)


def write_stl_binary(path, tri):
    n = len(tri)
    v1, v2, v3 = tri[:, 0], tri[:, 1], tri[:, 2]
    nrm = np.cross(v2 - v1, v3 - v1)
    lens = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = np.divide(nrm, lens, out=np.zeros_like(nrm), where=lens > 0)
    rec = np.zeros(n, dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = nrm, tri
    with open(path, "wb") as f:
        f.write(b"\0" * 80)
        f.write(struct.pack("<I", n))
        f.write(rec.tobytes())


def parse_protect(s):
    tag, rest = s.split(":", 1)
    p = rest.split(",")
    v = list(map(float, p[:8]))
    return {
        "type": tag,
        "center": np.array(v[0:3]),
        "axis": np.array(v[3:6]) / np.linalg.norm(v[3:6]),
        "d": v[6],
        "depth": v[7] if v[7] > 0 else 1e4,
        "extent": p[8] if len(p) > 8 else "through",
    }


def cmd_info(args):
    tri = read_stl(args.input)
    lo, hi = tri.reshape(-1, 3).min(0), tri.reshape(-1, 3).max(0)
    print(json.dumps({
        "triangles": len(tri),
        "dimensions_mm": [round(float(x), 3) for x in hi - lo],
        "bounds_min": [round(float(x), 3) for x in lo],
        "bounds_max": [round(float(x), 3) for x in hi],
    }, indent=2))


def cmd_scale(args):
    tri = read_stl(args.input)
    pts = tri.reshape(-1, 3)
    protects = [parse_protect(s) for s in args.protect]
    center = pts.mean(axis=0)

    masks = []
    for f in protects:
        mid = f["center"] + f["axis"] * (f["depth"] / 2 if f["extent"] == "blind" else 0)
        half = f["depth"] / 2
        rel = pts - mid
        axial = rel @ f["axis"]
        radial = np.linalg.norm(rel - np.outer(axial, f["axis"]), axis=1)
        masks.append((np.abs(axial) <= half + 0.05)
                     & (np.abs(radial - f["d"] / 2) <= 0.15))

    pts = (pts - center) * args.scale + center

    for f, mask in zip(protects, masks):
        if not mask.any():
            print(f"WARNING: no wall vertices for feature d={f['d']}", file=sys.stderr)
            continue
        mid = f["center"] + f["axis"] * (f["depth"] / 2 if f["extent"] == "blind" else 0)
        mid_s = (mid - center) * args.scale + center
        rel = pts[mask] - mid_s
        axial = rel @ f["axis"]
        rad = rel - np.outer(axial, f["axis"])
        rad_u = rad / np.linalg.norm(rad, axis=1)[:, None]
        pts[mask] = mid_s + np.outer(axial, f["axis"]) + rad_u * (f["d"] / 2)

        # blind holes (magnet pockets): restore original depth too —
        # compress axial coords of everything inside the scaled pocket
        if f["extent"] == "blind" and f["depth"] < 1e3:
            opening_s = (f["center"] - center) * args.scale + center
            rel = pts - opening_s
            axial = rel @ f["axis"]
            radial = np.linalg.norm(rel - np.outer(axial, f["axis"]), axis=1)
            pocket = (radial <= f["d"] / 2 + 0.15) & (axial > 0.01) \
                & (axial <= f["depth"] * args.scale + 0.05)
            pts[pocket] -= np.outer(axial[pocket] * (1 - 1 / args.scale), f["axis"])

    write_stl_binary(args.output, pts.reshape(-1, 3, 3))
    lo, hi = pts.min(0), pts.max(0)
    print(json.dumps({
        "scale": args.scale,
        "protected_features": len(protects),
        "dims_after_mm": [round(float(x), 2) for x in hi - lo],
        "output": args.output,
    }, indent=2))


MODEL_XML = """<?xml version="1.0" encoding="UTF-8"?>
<model unit="millimeter" xml:lang="en-US"
 xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">
 <resources>{materials}
  <object id="1" type="model"{pid}>
   <mesh>
    <vertices>
{verts}
    </vertices>
    <triangles>
{tris}
    </triangles>
   </mesh>
  </object>
 </resources>
 <build><item objectid="1"/></build>
</model>"""

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel-1"
  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>"""


def cmd_to3mf(args):
    tri = read_stl(args.input)
    pts = tri.reshape(-1, 3)
    uniq, inv = np.unique(np.round(pts, 6), axis=0, return_inverse=True)
    faces = inv.reshape(-1, 3)
    verts = "\n".join(
        f'     <vertex x="{v[0]:.6f}" y="{v[1]:.6f}" z="{v[2]:.6f}"/>' for v in uniq)
    tris = "\n".join(
        f'     <triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>' for f in faces)
    materials, pid = "", ""
    if args.color:
        materials = ('\n  <basematerials id="2">'
                     f'<base name="Color" displaycolor="{args.color.upper()}FF"/>'
                     "</basematerials>")
        pid = ' pid="2" pindex="0"'
    xml = MODEL_XML.format(materials=materials, pid=pid, verts=verts, tris=tris)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("3D/3dmodel.model", xml)
    print(f"wrote {args.output}: {len(uniq)} vertices, {len(faces)} triangles")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("info"); p.add_argument("input"); p.set_defaults(func=cmd_info)
    p = sub.add_parser("scale")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--scale", type=float, required=True)
    p.add_argument("--protect", action="append", default=[])
    p.set_defaults(func=cmd_scale)
    p = sub.add_parser("to3mf")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--color", default=None)
    p.set_defaults(func=cmd_to3mf)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
