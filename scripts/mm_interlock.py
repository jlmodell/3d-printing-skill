#!/usr/bin/env python3
"""Multi-material mechanical interlocks (soft TPU <-> rigid PETG/PLA), build123d.

Why this exists: slicer beam interlocking is a good second layer, but it is
silently skipped in thin parts (boundary avoidance), between separate objects,
and under height-range modifiers. A lock that is *designed into the geometry*
holds even when the slicer adds nothing and even if the two plastics never fuse.
Read references/multimaterial_interlock.md before changing a default here.

Library use (build123d >= 0.5):

    from mm_interlock import LockSpec, mushroom_peg, dovetail_seam, rivet, \
        apply_lock, grid_points, verify_pair, export_parts_3mf

    spec = LockSpec.for_nozzle(0.4)            # or 0.2
    pegs = [Pos(x, y, 2.0) * mushroom_peg(spec, length=1.6, direction=-1)
            for x, y in grid_points(...)]
    art, body = apply_lock(owner=art, other=body, features=pegs)
    verify_pair(art, body)                      # no overlap, real contact
    export_parts_3mf("charm.3mf", [("body_TPU", body, 1), ("art_PLA", art, 2)])

The owner gets the features fused on; the other body gets exactly the same
volume cut out. The two bodies therefore share a boundary with zero gap and
zero overlap, which is what both slicers need to treat them as touching
regions of one object.

CLI smoke test:

    python scripts/mm_interlock.py demo --nozzle 0.4 --out <output-dir>
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import tempfile
import uuid
import zipfile
from dataclasses import dataclass, asdict, replace
from typing import Iterable, Sequence

try:
    from build123d import (Align, Box, Cylinder, Part, Plane, Polygon, Pos,
                           Rot, Solid, export_stl, extrude, Compound)
except ImportError as exc:  # pragma: no cover
    sys.exit("build123d is required: pip install build123d "
             f"(or use server/.venv/bin/python). {exc}")

CENTER_BOTTOM = (Align.CENTER, Align.CENTER, Align.MIN)


# --------------------------------------------------------------------------
# Defaults per nozzle. Every number is a multiple of the extrusion width (w)
# or the layer height (h) so the slicer can actually draw it. See the
# reference file for the derivation and the sources.
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class LockSpec:
    nozzle: float          # mm
    layer: float           # mm, typical layer height for this nozzle
    line: float            # mm, extrusion width the slicer will use
    min_wall: float        # rigid wall left around any lock feature (3 lines)
    # mushroom peg (round undercut key)
    peg_neck_d: float      # neck diameter, >= ~5 lines so a soft neck is solid
    peg_head_d: float      # head diameter = neck + 2 x undercut
    peg_head_h: float      # head thickness (layers)
    peg_pitch: float       # centre-to-centre spacing
    # dovetail tab (in-plane, extruded in Z)
    dt_neck_w: float
    dt_head_w: float
    dt_depth: float        # how far the tab reaches into the other body
    dt_pitch: float
    # rivet (soft material flows through a hole in the rigid plate, caps it)
    rv_bore_d: float
    rv_cap_d: float
    rv_cap_h: float        # counterbore depth on the far side (layers)
    rv_pitch: float
    # skin of the capturing body kept above/below a buried lock
    cover: float

    @property
    def undercut(self) -> float:
        return (self.peg_head_d - self.peg_neck_d) / 2

    @classmethod
    def for_nozzle(cls, nozzle: float = 0.4, layer: float | None = None) -> "LockSpec":
        if abs(nozzle - 0.4) < 1e-6:
            base = _SPEC_04
        elif abs(nozzle - 0.2) < 1e-6:
            base = _SPEC_02
        else:
            # scale linearly from the 0.4 set; flag it, do not pretend it is tuned
            k = nozzle / 0.4
            base = cls(**{f: (v * k if isinstance(v, float) else v)
                          for f, v in asdict(_SPEC_04).items()})
            print(f"[mm_interlock] nozzle {nozzle}: scaled from the 0.4 set "
                  "(UNTESTED) - print the coupon first", file=sys.stderr)
        if layer is not None:
            base = replace(base, layer=layer)
        return base


# 0.4 nozzle: w = 0.42 (Bambu/Orca default line width for 0.4), h = 0.2
_SPEC_04 = LockSpec(
    nozzle=0.4, layer=0.2, line=0.42, min_wall=1.2,
    peg_neck_d=2.4, peg_head_d=3.6, peg_head_h=0.8, peg_pitch=6.0,
    dt_neck_w=3.0, dt_head_w=4.6, dt_depth=3.0, dt_pitch=8.0,
    rv_bore_d=2.0, rv_cap_d=3.6, rv_cap_h=0.6, rv_pitch=6.0,
    cover=0.8,
)
# 0.2 nozzle: w = 0.22, h = 0.1 (0.08-0.12 typical)
_SPEC_02 = LockSpec(
    nozzle=0.2, layer=0.1, line=0.22, min_wall=0.66,
    peg_neck_d=1.4, peg_head_d=2.2, peg_head_h=0.5, peg_pitch=3.6,
    dt_neck_w=1.6, dt_head_w=2.6, dt_depth=1.8, dt_pitch=4.6,
    rv_bore_d=1.2, rv_cap_d=2.2, rv_cap_h=0.4, rv_pitch=3.6,
    cover=0.5,
)


# --------------------------------------------------------------------------
# Lock features. Each returns a solid in local coordinates; place it with
# Pos()/Rot(). The feature is the volume that belongs to the OWNER body.
# --------------------------------------------------------------------------
def mushroom_peg(spec: LockSpec, length: float, direction: int = -1,
                 neck_d: float | None = None, head_d: float | None = None,
                 head_h: float | None = None) -> Part:
    """Round undercut key. Starts at z=0 (the shared face) and reaches
    `length` into the other body, along -Z (direction=-1, owner on top, e.g.
    rigid art pegging down into a TPU body) or +Z (direction=+1).

    The head is a flat-shouldered undercut, not a cone: the other material
    is printed around and over the shoulder, so there is no overhang to
    support, and a flat shoulder resists pull-out far better than a taper.
    """
    nd = neck_d or spec.peg_neck_d
    hd = head_d or spec.peg_head_d
    hh = head_h or spec.peg_head_h
    if length <= hh + spec.layer:
        raise ValueError(f"peg length {length} must exceed head {hh} + one layer")
    neck_len = length - hh
    neck = Cylinder(nd / 2, neck_len + 0.01, align=CENTER_BOTTOM)  # 0.01 fuses into owner face
    head = Pos(0, 0, neck_len) * Cylinder(hd / 2, hh, align=CENTER_BOTTOM)
    peg = Pos(0, 0, -0.01) * (neck + head)
    if direction < 0:
        peg = Rot(180, 0, 0) * peg
    return peg


def dovetail_tab(spec: LockSpec, z0: float, z1: float,
                 neck_w: float | None = None, head_w: float | None = None,
                 depth: float | None = None) -> Part:
    """One in-plane dovetail. Neck sits on y=0 (the seam), flares to the head
    at y=depth (into the other body). Extruded from z0 to z1.

    Keep z0/z1 inside the other body (>= spec.cover from its top and bottom
    faces) to make the tab *buried*: then it is locked in X, Y and Z.
    """
    nw = neck_w or spec.dt_neck_w
    hw = head_w or spec.dt_head_w
    d = depth or spec.dt_depth
    e = 0.01  # fuse into the owner side of the seam
    pts = [(-nw / 2, -e), (nw / 2, -e), (hw / 2, d), (-hw / 2, d)]
    prof = Plane.XY.offset(z0) * Polygon(*pts, align=None)
    return extrude(prof, amount=z1 - z0)


def dovetail_seam(spec: LockSpec, x0: float, x1: float, y: float,
                  z0: float, z1: float, into: int = +1, **kw) -> list[Part]:
    """Dovetail tabs along a straight seam y=const from x0 to x1, pointing
    into +Y (into=+1) or -Y (into=-1). Tabs are centred and evenly pitched,
    with >= min_wall + half a head kept clear at each end."""
    hw = kw.get("head_w") or spec.dt_head_w
    usable = (x1 - x0) - 2 * spec.min_wall - hw
    n = max(1, int(usable // spec.dt_pitch) + 1)
    span = (n - 1) * spec.dt_pitch
    xc = (x0 + x1) / 2
    tabs = []
    for i in range(n):
        x = xc - span / 2 + i * spec.dt_pitch
        t = dovetail_tab(spec, z0, z1, **kw)
        if into < 0:
            t = Rot(0, 0, 180) * t
        tabs.append(Pos(x, y, 0) * t)
    return tabs


def rivet(spec: LockSpec, plate_t: float, bore_d: float | None = None,
          cap_d: float | None = None, cap_h: float | None = None) -> Part:
    """Soft-material rivet through a rigid plate of thickness plate_t that sits
    on z in [0, plate_t]. The soft body is below z=0; the rivet fills the bore
    and spreads into a counterbore on the TOP side (z = plate_t - cap_h ..
    plate_t), so the plate cannot lift off. Owner = the SOFT body.
    Flip with Rot(180,0,0) for soft-on-top."""
    bd = bore_d or spec.rv_bore_d
    cd = cap_d or spec.rv_cap_d
    ch = cap_h or spec.rv_cap_h
    if plate_t < ch + 2 * spec.layer:
        raise ValueError(f"plate {plate_t} too thin for a {ch} cap + 2 layers of grip")
    e = 0.01
    bore = Pos(0, 0, -e) * Cylinder(bd / 2, plate_t + e, align=CENTER_BOTTOM)
    cap = Pos(0, 0, plate_t - ch) * Cylinder(cd / 2, ch, align=CENTER_BOTTOM)
    return bore + cap


def grid_points(xmin: float, xmax: float, ymin: float, ymax: float,
                pitch: float, margin: float) -> list[tuple[float, float]]:
    """Centred grid of feature positions inside a rectangle, keeping `margin`
    (feature radius + min_wall) from every edge."""
    def axis(a, b):
        usable = (b - a) - 2 * margin
        if usable < 0:
            return []
        n = int(usable // pitch) + 1
        span = (n - 1) * pitch
        c = (a + b) / 2
        return [c - span / 2 + i * pitch for i in range(n)]
    return [(x, y) for x in axis(xmin, xmax) for y in axis(ymin, ymax)]


def apply_lock(owner, other, features: Iterable):
    """Fuse features onto `owner`, cut the same volume out of `other`.
    Returns (owner, other). Zero gap, zero overlap by construction."""
    feats = list(features)
    if not feats:
        return owner, other
    tool = feats[0]
    for f in feats[1:]:
        tool = tool + f
    owner2 = owner + tool
    other2 = other - tool
    return owner2, other2


def _volume(shape) -> float:
    try:
        return float(shape.volume)
    except Exception:
        return 0.0


def verify_pair(a, b, tol: float = 1e-3, name_a: str = "A", name_b: str = "B") -> dict:
    """Assert the two bodies do not overlap and do touch. Returns numbers."""
    inter = _volume(a & b)
    # contact: grow nothing; check that the union is one connected solid
    u = a + b
    solids = len(u.solids()) if hasattr(u, "solids") else 1
    res = {"overlap_mm3": round(inter, 5), f"{name_a}_mm3": round(_volume(a), 3),
           f"{name_b}_mm3": round(_volume(b), 3), "union_solids": solids}
    if inter > tol:
        raise AssertionError(f"{name_a} and {name_b} overlap by {inter:.4f} mm3: {res}")
    if solids != 1:
        raise AssertionError(f"{name_a} and {name_b} do not touch (union has {solids} solids): {res}")
    return res


def check_min_wall(spec: LockSpec, edge_clearance: float) -> None:
    """Raise if a feature sits closer than min_wall to a free edge."""
    if edge_clearance + 1e-9 < spec.min_wall:
        raise ValueError(f"lock feature {edge_clearance:.2f} mm from an edge; "
                         f"floor is {spec.min_wall} mm (3 lines at {spec.nozzle})")


# --------------------------------------------------------------------------
# Export: one OBJECT with several PARTS (one per material). Bambu Studio and
# Orca (incl. Snapmaker Orca) only interlock between parts of the same object.
# --------------------------------------------------------------------------
def _mesh(shape, tol=0.01, ang=0.2):
    import trimesh  # noqa: WPS433
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "m.stl")
        export_stl(shape, p, tolerance=tol, angular_tolerance=ang)
        m = trimesh.load(p, force="mesh")
    m.merge_vertices()
    return m


def export_parts_3mf(path: str, parts: Sequence[tuple], object_name: str = "interlocked",
                     stl_dir: str | None = None) -> dict:
    """Write a 3MF with ONE object made of named parts.

    parts: [(name, shape, extruder_int), ...]. The extruder number is written
    into Metadata/model_settings.config (Bambu Studio / Orca read it) so each
    part opens on its own filament slot. No printer, process or filament
    profile is written: pick those in the slicer (never fabricate one).
    Also writes one STL per part to stl_dir if given (Kobra X / other slicers:
    import the STLs together and answer "yes" to "load as a single object
    with multiple parts").
    """
    return export_objects_3mf(path, [(object_name, parts)], stl_dir=stl_dir)["objects"][0] | {"path": path}


def export_objects_3mf(path: str, objects: Sequence[tuple], gap: float = 6.0,
                       stl_dir: str | None = None) -> dict:
    """Several multi-part objects on one plate, laid out in a column along Y.
    objects: [(object_name, [(part_name, shape, extruder), ...]), ...]."""
    import numpy as np
    res_xml, build_xml, cfg_xml, report = [], [], [], []
    next_id = 1
    y_cursor = 0.0
    built = []
    for oname, parts in objects:
        meshes = []
        for item in parts:
            name, shape, ext = item[0], item[1], int(item[2])
            m = _mesh(shape)
            if not m.is_watertight:
                raise AssertionError(f"{oname}/{name} is not watertight after tessellation")
            meshes.append((name, m, ext))
            if stl_dir:
                os.makedirs(stl_dir, exist_ok=True)
                m.export(os.path.join(stl_dir, f"{oname}_{name}.stl"))
        allv = np.vstack([m.vertices for _, m, _ in meshes])
        lo, hi = allv.min(0), allv.max(0)
        built.append((oname, meshes, lo, hi))
    total_y = sum(h[1] - l[1] for _, _, l, h in built) + gap * (len(built) - 1)
    y_cursor = -total_y / 2
    for oname, meshes, lo, hi in built:
        # local frame: centred on X/Y, resting on z=0; the build item places it
        shift = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
        comps, cfg_parts = [], []
        for name, m, ext in meshes:
            v = m.vertices + shift
            vs = "".join(f'<vertex x="{a:.5f}" y="{b:.5f}" z="{c:.5f}"/>' for a, b, c in v)
            ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in m.faces)
            res_xml.append(f'<object id="{next_id}" name="{name}" type="model" p:UUID="{uuid.uuid4()}">'
                           f'<mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
            comps.append(f'<component objectid="{next_id}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
            cfg_parts.append(
                f'    <part id="{next_id}" subtype="normal_part">\n'
                f'      <metadata key="name" value="{name}"/>\n'
                f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n'
                f'      <metadata key="extruder" value="{ext}"/>\n'
                f'    </part>\n')
            next_id += 1
        oid = next_id
        next_id += 1
        res_xml.append(f'<object id="{oid}" name="{oname}" type="model" p:UUID="{uuid.uuid4()}">'
                       f'<components>{"".join(comps)}</components></object>')
        dy = hi[1] - lo[1]
        cy = 128 + y_cursor + dy / 2
        y_cursor += dy + gap
        build_xml.append(f'<item objectid="{oid}" p:UUID="{uuid.uuid4()}" '
                         f'transform="1 0 0 0 1 0 0 0 1 128 {cy:.3f} 0" printable="1"/>')
        cfg_xml.append(f'  <object id="{oid}">\n'
                       f'    <metadata key="name" value="{oname}"/>\n'
                       f'    <metadata key="extruder" value="{meshes[0][2]}"/>\n'
                       + "".join(cfg_parts) + '  </object>\n')
        report.append({"object": oname,
                       "parts": [(n, e, round(float(m.volume), 3)) for n, m, e in meshes],
                       "size_mm": [round(float(x), 2) for x in (hi - lo)]})
    model = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n'
        '<metadata name="Application">mm_interlock.py</metadata>\n'
        f'<resources>{"".join(res_xml)}</resources>\n'
        f'<build p:UUID="{uuid.uuid4()}">{"".join(build_xml)}</build>\n'
        '</model>\n')
    cfg = '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + "".join(cfg_xml) + '</config>\n'
    ctypes = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
              '<Default Extension="config" ContentType="text/xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel-1" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ctypes)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/model_settings.config", cfg)
    return {"path": path, "objects": report}


# --------------------------------------------------------------------------
def _demo(args):
    spec = LockSpec.for_nozzle(args.nozzle)
    # rigid PETG plate on a TPU pad, side seam with dovetails + pegs from the plate
    W, L, T = 30.0, 20.0, 3.0
    body = Box(W, L, T, align=(Align.MIN, Align.MIN, Align.MIN))
    rigid = Pos(0, L, 0) * Box(W, 12, T, align=(Align.MIN, Align.MIN, Align.MIN))
    tabs = dovetail_seam(spec, 0, W, L, spec.cover, T - spec.cover, into=-1)
    rigid, body = apply_lock(rigid, body, tabs)
    print("demo:", verify_pair(rigid, body, name_a="rigid", name_b="soft"))
    os.makedirs(args.out, exist_ok=True)
    info = export_parts_3mf(os.path.join(args.out, f"mm_interlock_demo_{args.nozzle}.3mf"),
                            [("soft_TPU", body, 1), ("rigid_PETG", rigid, 2)],
                            object_name="mm_interlock_demo", stl_dir=args.out)
    print(info)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("demo", help="build and export a small locked pair")
    d.add_argument("--nozzle", type=float, default=0.4)
    d.add_argument("--out", default="mm_interlock_out")
    d.set_defaults(func=_demo)
    s = sub.add_parser("spec", help="print the default lock dimensions")
    s.add_argument("--nozzle", type=float, default=0.4)
    s.set_defaults(func=lambda a: [print(f"{k:12s} {v}") for k, v in asdict(LockSpec.for_nozzle(a.nozzle)).items()])
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
