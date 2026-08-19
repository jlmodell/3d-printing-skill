#!/usr/bin/env python3
"""Scale a model while keeping hardware interfaces at their original size.

Usage:
  python smart_scale.py in.stl out.3mf --scale 1.5 \
      --protect "cyl:cx,cy,cz,ax,ay,az,diameter,depth,through" \
      --protect "cyl:...,blind" [--mode recut|project] [--origin centroid|world]

--protect strings come straight from detect_features.py's `protect_arg` field.
  cyl:  = a hole to preserve (diameter and, for blind holes, depth kept)
  boss: = a protruding cylinder to preserve (e.g. printed shaft into a bearing)

Modes:
  recut (default): plug each protected hole, scale, re-cut at original size.
      Needs manifold3d. Robust for any scale; changes topology (kills 3MF paint).
  project: scale, then radially project hole-wall vertices back to original
      radius. Topology-preserving (keeps paint); best for modest scales and
      plain cylindrical holes.
"""
import argparse
import json
import sys

import numpy as np
import trimesh


def parse_protect(s):
    tag, rest = s.split(":", 1)
    parts = rest.split(",")
    vals = list(map(float, parts[:8]))
    extent = parts[8] if len(parts) > 8 else "through"
    return {
        "type": tag,
        "center": np.array(vals[0:3]),
        "axis": np.array(vals[3:6]) / np.linalg.norm(vals[3:6]),
        "d": vals[6],
        "depth": vals[7],
        "extent": extent,
    }


def cylinder_at(center, axis, radius, height, sections=96):
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    # cylinder is centered at origin along +Z; rotate Z to axis, move to center
    T = trimesh.geometry.align_vectors([0, 0, 1], axis)
    cyl.apply_transform(T)
    cyl.apply_translation(center)
    return cyl


def feature_span(f, mesh_scale_hint=1.0):
    """(midpoint_center, height) covering the feature with margin."""
    depth = f["depth"] if f["depth"] > 0 else 20.0
    if f["extent"] == "through":
        # center given at mid-depth by detector for through holes
        return f["center"], depth
    # blind: center is at the opening, axis points into the hole
    mid = f["center"] + f["axis"] * depth / 2
    return mid, depth


def recut(mesh, scale, protects, origin):
    from trimesh import boolean

    plugs, cutters = [], []
    for f in protects:
        mid, depth = feature_span(f)
        r = f["d"] / 2
        if f["type"] == "cyl":
            # plug generously (radially and axially for through holes)
            extra = depth * scale + 4 if f["extent"] == "through" else depth + 2
            plugs.append(cylinder_at(mid, f["axis"], r + 0.4, extra))
        # boss: nothing to plug; we re-cut the *surroundings*? No — bosses are
        # handled by cutting away scaled boss and unioning original-size boss.

    solid = mesh
    if plugs:
        solid = boolean.union([solid] + plugs, engine="manifold")

    # capture original-size boss geometry before scaling
    boss_copies = []
    for f in protects:
        if f["type"] == "boss":
            mid, depth = feature_span(f)
            boss_copies.append(
                (f, cylinder_at(mid, f["axis"], f["d"] / 2, depth + 0.02))
            )

    center = mesh.centroid if origin == "centroid" else np.zeros(3)
    M = trimesh.transformations.scale_matrix(scale, center)
    solid.apply_transform(M)

    def xform_point(p):
        return (p - center) * scale + center

    for f in protects:
        mid, depth = feature_span(f)
        mid_s = xform_point(mid)
        r = f["d"] / 2
        if f["type"] == "cyl":
            if f["extent"] == "through":
                h = depth * scale + 4  # must fully pierce the scaled body
                cutters.append(cylinder_at(mid_s, f["axis"], r, h))
            else:
                # preserve original depth, measured from the (scaled) opening
                opening_s = xform_point(f["center"])
                mid_new = opening_s + f["axis"] * (depth / 2 - 0.01)
                cutters.append(cylinder_at(mid_new, f["axis"], r, depth + 0.02))
        else:  # boss: remove the scaled boss, restore original-size boss
            h_rm = depth * scale + 0.5
            base_s = xform_point(f["center"])
            mid_rm = base_s + f["axis"] * (depth * scale) / 2
            cutters.append(cylinder_at(mid_rm, f["axis"], (r * scale) + 0.4, h_rm))

    if cutters:
        solid = boolean.difference([solid] + cutters, engine="manifold")

    for f, orig_boss in boss_copies:
        base_s = xform_point(f["center"])
        orig_boss.apply_translation(base_s - f["center"])
        solid = boolean.union([solid, orig_boss], engine="manifold")

    return solid


def project(mesh, scale, protects, origin):
    center = mesh.centroid if origin == "centroid" else np.zeros(3)
    v = mesh.vertices.copy()

    # record, per protected feature, which vertices are on its wall (pre-scale)
    masks = []
    for f in protects:
        mid, depth = feature_span(f)
        r = f["d"] / 2
        rel = v - mid
        axial = rel @ f["axis"]
        radial = np.linalg.norm(rel - np.outer(axial, f["axis"]), axis=1)
        mask = (np.abs(axial) <= depth / 2 + 0.05) & (np.abs(radial - r) <= 0.15)
        masks.append(mask)

    v = (v - center) * scale + center

    for f, mask in zip(protects, masks):
        if not mask.any():
            print(f"WARNING: no wall vertices found for feature d={f['d']}",
                  file=sys.stderr)
            continue
        mid, depth = feature_span(f)
        mid_s = (mid - center) * scale + center
        r = f["d"] / 2
        rel = v[mask] - mid_s
        axial = rel @ f["axis"]
        rad_vec = rel - np.outer(axial, f["axis"])
        rad_len = np.linalg.norm(rad_vec, axis=1)
        rad_unit = rad_vec / rad_len[:, None]
        v[mask] = mid_s + np.outer(axial, f["axis"]) + rad_unit * r

        # blind holes (magnet pockets): restore original depth too
        if f["extent"] == "blind" and 0 < f["depth"] < 1e3:
            opening_s = (f["center"] - center) * scale + center
            rel_all = v - opening_s
            ax_all = rel_all @ f["axis"]
            rad_all = np.linalg.norm(
                rel_all - np.outer(ax_all, f["axis"]), axis=1)
            pocket = (rad_all <= r + 0.15) & (ax_all > 0.01) \
                & (ax_all <= f["depth"] * scale + 0.05)
            v[pocket] -= np.outer(ax_all[pocket] * (1 - 1 / scale), f["axis"])
    mesh = mesh.copy()
    mesh.vertices = v
    return mesh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--scale", type=float, required=True)
    ap.add_argument("--protect", action="append", default=[])
    ap.add_argument("--mode", choices=["recut", "project"], default="recut")
    ap.add_argument("--origin", choices=["centroid", "world"], default="centroid")
    args = ap.parse_args()

    loaded = trimesh.load(args.input)
    mesh = loaded.to_mesh() if isinstance(loaded, trimesh.Scene) else loaded
    protects = [parse_protect(s) for s in args.protect]

    if args.mode == "recut" and protects:
        if not mesh.is_watertight:
            trimesh.repair.fill_holes(mesh)
            trimesh.repair.fix_normals(mesh)
            if not mesh.is_watertight:
                sys.exit("Mesh not watertight; repair failed. Try --mode project "
                         "or repair the mesh first.")
        result = recut(mesh, args.scale, protects, args.origin)
    elif protects:
        result = project(mesh, args.scale, protects, args.origin)
    else:
        center = mesh.centroid if args.origin == "centroid" else np.zeros(3)
        result = mesh.copy()
        result.apply_transform(
            trimesh.transformations.scale_matrix(args.scale, center))

    result.export(args.output)
    dims_in = (loaded.bounds[1] - loaded.bounds[0])
    dims_out = (result.bounds[1] - result.bounds[0])
    print(json.dumps({
        "scale": args.scale, "mode": args.mode,
        "protected_features": len(protects),
        "dims_before_mm": [round(float(x), 2) for x in dims_in],
        "dims_after_mm": [round(float(x), 2) for x in dims_out],
        "watertight": bool(result.is_watertight),
        "output": args.output,
    }, indent=2))


if __name__ == "__main__":
    main()
