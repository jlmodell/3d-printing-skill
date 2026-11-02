#!/usr/bin/env python3
"""Printable multi-material interlock test coupons (soft TPU + rigid PETG/PLA).

Print ONE plate of these before trusting any new material pair, nozzle,
printer or slicer setting for a bonded multi-material part. Each coupon is a
single object with two parts (soft = filament slot 1, rigid = slot 2 by
default), so the slicer's beam interlocking can act on it.

    python scripts/interlock_coupon.py --nozzle 0.4 --out <dir>
    python scripts/interlock_coupon.py --nozzle 0.2 --thickness 2.0 --out <dir>
    python scripts/interlock_coupon.py --only butt,dovetail --soft-slot 1 --rigid-slot 3

Variants (rigid end carries 1..N notches = the number below, so they can be
told apart after printing):
  1 butt      side-by-side, straight seam. Control: only the slicer beams hold it.
  2 dovetail  side-by-side, buried dovetail tabs from the rigid side.
  3 pegs      rigid plate on top of a soft base, mushroom pegs down into it,
              plate sunk into the base (stacked interface - charm art on base).
  4 flat      same stack as 3 with no pegs (control for 3).
  5 rivet     rigid plate on top of a soft base, soft rivets up through the
              plate with a cap in a counterbore (soft-over-rigid "stitches").

Outputs: interlock_coupons_<nozzle>.3mf (all variants, one object each, with
per-part filament slots) + one STL per part (for slicers that ignore 3MF
part metadata). Read references/multimaterial_interlock.md for how to print
and score them.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mm_interlock import (LockSpec, apply_lock, dovetail_seam, export_objects_3mf,  # noqa: E402
                          grid_points, mushroom_peg, rivet, verify_pair, check_min_wall)
from build123d import Align, Box, Cylinder, Pos  # noqa: E402

MIN3 = (Align.MIN, Align.MIN, Align.MIN)
CB = (Align.CENTER, Align.CENTER, Align.MIN)


def _scale(spec: LockSpec) -> float:
    return 1.0 if spec.nozzle >= 0.4 else 0.6


def _pull_hole(body, x, y, t, d):
    return body - Pos(x, y, -0.1) * Cylinder(d / 2, t + 0.2, align=CB)


def _notches(body, x_end, y0, w, t, n, spec):
    """n small V-free rectangular notches on the rigid end face for ID."""
    nw, nd = 3 * spec.line, 3 * spec.line
    pitch = nw * 2.2
    span = (n - 1) * pitch
    for i in range(n):
        y = y0 + w / 2 - span / 2 + i * pitch
        body = body - Pos(x_end - nd, y - nw / 2, -0.1) * Box(nd + 0.1, nw, t + 0.2, align=MIN3)
    return body


def side_by_side(spec, t, lock: bool, n_id: int):
    k = _scale(spec)
    L, W = 30 * k, 12 * k
    hole = 4.0 * k
    soft = Box(L, W, t, align=MIN3)
    rigid = Pos(L, 0, 0) * Box(L, W, t, align=MIN3)
    if lock:
        cover = spec.cover
        if t - 2 * cover < 2 * spec.layer:
            cover = max(spec.layer, (t - 2 * spec.layer) / 2)
            print(f"[coupon] dovetail: thin strip, cover cut to {cover:.2f} mm", file=sys.stderr)
        from build123d import Rot
        # build the seam along X pointing +Y, then Rot z+90 (+Y -> -X, x -> y):
        # tabs leave the rigid half at x=L and reach -X into the soft half.
        tabs = dovetail_seam(spec, 0, W, 0, cover, t - cover, into=+1)
        tabs = [Pos(L, 0, 0) * Rot(0, 0, 90) * tb for tb in tabs]
        rigid, soft = apply_lock(rigid, soft, tabs)
    soft = _pull_hole(soft, 0.25 * L, W / 2, t, hole)
    rigid = _pull_hole(rigid, 1.75 * L, W / 2, t, hole)
    rigid = _notches(rigid, 2 * L, 0, W, t, n_id, spec)
    return soft, rigid


def stacked(spec, base_t, mode: str, n_id: int, sink: float | None = None,
            plate_t: float | None = None):
    k = _scale(spec)
    BL, BW = 30 * k, 20 * k
    PL, PW = 20 * k, 12 * k
    sink = spec.cover if sink is None else sink                  # art sunk into base
    plate_t = (1.6 if spec.nozzle >= 0.4 else 1.0) if plate_t is None else plate_t
    soft = Box(BL, BW, base_t, align=MIN3)
    z0 = base_t - sink                                           # plate bottom
    px0, py0 = (BL - PL) / 2, (BW - PW) / 2
    rigid = Pos(px0, py0, z0) * Box(PL, PW, plate_t, align=MIN3)
    soft = soft - rigid                                          # pocket for the sunk plate
    feats = []
    if mode == "pegs":
        r = spec.peg_head_d / 2
        margin = r + spec.min_wall
        check_min_wall(spec, (min(PL, PW) / 2) - r)
        plen = min(spec.peg_head_h + 4 * spec.layer, z0 - spec.cover)
        if plen < spec.peg_head_h + 2 * spec.layer:
            raise ValueError(f"soft base {base_t} mm too thin for pegs: need >= "
                             f"{sink + spec.peg_head_h + 2 * spec.layer + spec.cover:.2f} mm")
        for x, y in grid_points(px0, px0 + PL, py0, py0 + PW, spec.peg_pitch, margin):
            feats.append(Pos(x, y, z0) * mushroom_peg(spec, plen, direction=-1))
        rigid, soft = apply_lock(rigid, soft, feats)
    elif mode == "rivet":
        r = spec.rv_cap_d / 2
        for x, y in grid_points(px0, px0 + PL, py0, py0 + PW, spec.rv_pitch, r + spec.min_wall):
            feats.append(Pos(x, y, z0) * rivet(spec, plate_t))
        soft, rigid = apply_lock(soft, rigid, feats)
    # ID: notches on the soft base's right end (rigid plate is inside the base)
    soft = _notches(soft, BL, 0, BW, base_t, n_id, spec)
    return soft, rigid, len(feats)


VARIANTS = ["butt", "dovetail", "pegs", "flat", "rivet"]


def build(nozzle=0.4, thickness=None, base=None, only=None, soft_slot=1, rigid_slot=2,
          out=".", soft_name="TPU", rigid_name="PETG"):
    spec = LockSpec.for_nozzle(nozzle)
    t = thickness or (3.0 if nozzle >= 0.4 else 2.0)
    bt = base or (3.0 if nozzle >= 0.4 else 2.0)
    want = only or VARIANTS
    objs, summary = [], []
    for idx, v in enumerate(VARIANTS, start=1):
        if v not in want:
            continue
        nfeat = None
        if v in ("butt", "dovetail"):
            soft, rigid = side_by_side(spec, t, v == "dovetail", idx)
        else:
            soft, rigid, nfeat = stacked(spec, bt, v, idx)
        chk = verify_pair(soft, rigid, name_a="soft", name_b="rigid")
        name = f"c{idx}_{v}"
        objs.append((name, [(f"soft_{soft_name}", soft, soft_slot),
                            (f"rigid_{rigid_name}", rigid, rigid_slot)]))
        summary.append({"variant": v, "id_notches": idx, "lock_features": nfeat, **chk})
    path = os.path.join(out, f"interlock_coupons_{nozzle}.3mf")
    info = export_objects_3mf(path, objs, stl_dir=os.path.join(out, "stl"))
    return {"spec": spec.__dict__, "strip_thickness": t, "base_thickness": bt,
            "coupons": summary, "export": info}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--nozzle", type=float, default=0.4, help="0.4 or 0.2 (others scale, UNTESTED)")
    ap.add_argument("--thickness", type=float, help="side-by-side strip thickness (default 3.0 / 2.0)")
    ap.add_argument("--base", type=float, help="soft base thickness for stacked coupons (default 3.0 / 2.0)")
    ap.add_argument("--only", help="comma list of: " + ",".join(VARIANTS))
    ap.add_argument("--soft-slot", type=int, default=1)
    ap.add_argument("--rigid-slot", type=int, default=2)
    ap.add_argument("--soft-name", default="TPU")
    ap.add_argument("--rigid-name", default="PETG")
    ap.add_argument("--out", default="interlock_coupons")
    a = ap.parse_args()
    only = [s.strip() for s in a.only.split(",")] if a.only else None
    res = build(a.nozzle, a.thickness, a.base, only, a.soft_slot, a.rigid_slot, a.out,
                a.soft_name, a.rigid_name)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
