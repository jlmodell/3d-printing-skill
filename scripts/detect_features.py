#!/usr/bin/env python3
"""Detect cylindrical holes/bosses in a mesh and match them to known hardware.

Usage: python detect_features.py <file.stl|file.3mf> [--min-d 1.5] [--max-d 60]

Output: JSON list of features with center, axis, diameter, depth, kind
(hole/boss, through/blind) and candidate hardware matches. Feature strings
are printed in the exact format smart_scale.py accepts via --protect.

Method: circular sharp-edge loops are found where hole walls meet flat faces,
circles are fitted, coaxial pairs become through-features, singles are probed
for depth by ray casting. Works on typical CAD-exported meshes; organic or
very low-poly meshes may need manual measurement instead.
"""
import argparse
import json
import sys

import networkx as nx
import numpy as np
import trimesh

# Known hardware the user works with. Hole sizes in models = nominal + designed
# clearance, so matching uses a generous tolerance. Diameters in mm.
HARDWARE = [
    {"name": "magnet D5", "d": 5.0, "kind": "magnet"},
    {"name": "magnet D6 (common D6x2/D6x3)", "d": 6.0, "kind": "magnet"},
    {"name": "magnet D8 (common D8x3)", "d": 8.0, "kind": "magnet"},
    {"name": "magnet D10 / Bambu countersunk 10x4x3", "d": 10.0, "kind": "magnet"},
    {"name": "magnet D12 / Bambu countersunk 12x3x3", "d": 12.0, "kind": "magnet"},
    {"name": "clock movement shaft bushing (MH011-style, ~9mm thread)", "d": 9.0, "kind": "clock"},
    {"name": "clock hand shaft clearance", "d": 5.5, "kind": "clock"},
    {"name": "608 bearing OD", "d": 22.0, "kind": "bearing"},
    {"name": "608 bearing bore (8mm shaft)", "d": 8.0, "kind": "bearing"},
    {"name": "MR128 bearing OD", "d": 12.0, "kind": "bearing"},
    {"name": "6701 bearing OD", "d": 18.0, "kind": "bearing"},
    {"name": "M2 screw thread hole", "d": 2.0, "kind": "screw"},
    {"name": "M3 screw thread/clearance hole", "d": 3.2, "kind": "screw"},
    {"name": "M4 screw clearance hole", "d": 4.4, "kind": "screw"},
    {"name": "M3 heat-set insert hole", "d": 4.2, "kind": "insert"},
    {"name": "AA battery", "d": 14.5, "kind": "battery"},
]
MATCH_TOL = 0.45  # mm; models add 0.1-0.3mm clearance over nominal


def fit_circle(points):
    """Fit plane + circle. Returns (center, normal, radius, rms) or None."""
    c = points.mean(axis=0)
    p = points - c
    _, s, vt = np.linalg.svd(p, full_matrices=False)
    normal = vt[2]
    planarity = s[2] / (s[0] + 1e-12)
    if planarity > 0.05:
        return None
    # project to plane, fit circle algebraically (Kasa fit)
    u, v = vt[0], vt[1]
    x, y = p @ u, p @ v
    A = np.column_stack([2 * x, 2 * y, np.ones(len(x))])
    b = x**2 + y**2
    sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy, c2 = sol
    r = np.sqrt(c2 + cx**2 + cy**2)
    center = c + cx * u + cy * v
    rms = np.sqrt(np.mean((np.sqrt((x - cx) ** 2 + (y - cy) ** 2) - r) ** 2))
    if rms / r > 0.03:  # not circular
        return None
    return center, normal, r, rms


def sharp_edge_loops(mesh, angle=np.radians(25)):
    adj = mesh.face_adjacency
    ang = mesh.face_adjacency_angles
    edges = mesh.face_adjacency_edges[ang > angle]
    g = nx.Graph()
    g.add_edges_from(map(tuple, edges))
    loops = []
    for comp in nx.connected_components(g):
        sub = g.subgraph(comp)
        if all(d == 2 for _, d in sub.degree()) and 8 <= len(comp) <= 512:
            loops.append(list(nx.cycle_basis(sub)[0]) if nx.cycle_basis(sub) else None)
    return [l for l in loops if l]


def probe_depth(mesh, center, direction, max_depth=200.0):
    """Ray-cast from just inside a hole opening to find its bottom."""
    origin = center + direction * 0.05
    hits, _, _ = mesh.ray.intersects_location(
        ray_origins=[origin], ray_directions=[direction], multiple_hits=False
    )
    if len(hits):
        return float(np.linalg.norm(hits[0] - origin) + 0.05)
    return None


def classify(mesh, center, normal, r):
    """Decide hole vs boss and inward axis direction via containment tests."""
    for direction in (normal, -normal):
        axis_pt = center + direction * min(1.0, r)
        on_axis_inside = bool(mesh.contains([axis_pt])[0])
        ring_pt = center + direction * min(1.0, r)
        # material just outside the wall?
        wall_pt = ring_pt + np.array([1.0, 0, 0]) if abs(normal[0]) > 0.9 else ring_pt
        if not on_axis_inside:
            # empty along axis below the rim -> hole descending in `direction`
            return "hole", direction
    return "boss", normal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--min-d", type=float, default=1.5)
    ap.add_argument("--max-d", type=float, default=60.0)
    args = ap.parse_args()

    loaded = trimesh.load(args.file)
    mesh = (
        loaded.to_mesh() if isinstance(loaded, trimesh.Scene) else loaded
    )

    circles = []
    for loop in sharp_edge_loops(mesh):
        fit = fit_circle(mesh.vertices[loop])
        if fit is None:
            continue
        center, normal, r, rms = fit
        if not (args.min_d / 2 <= r <= args.max_d / 2):
            continue
        circles.append({"center": center, "normal": normal, "r": r})

    # pair coaxial same-radius circles -> through features
    used = set()
    features = []
    for i, a in enumerate(circles):
        if i in used:
            continue
        best = None
        for j in range(i + 1, len(circles)):
            if j in used:
                continue
            b = circles[j]
            if abs(a["r"] - b["r"]) > 0.02 * max(a["r"], 1):
                continue
            d = b["center"] - a["center"]
            dist = np.linalg.norm(d)
            if dist < 0.05:
                continue
            axis = d / dist
            if abs(abs(axis @ a["normal"])) < 0.98 or abs(abs(axis @ b["normal"])) < 0.98:
                continue
            best = (j, dist, axis)
            break
        if best:
            j, dist, axis = best
            used.update({i, j})
            mid = (a["center"] + circles[j]["center"]) / 2
            kind = "hole" if not mesh.contains([mid])[0] else "boss"
            features.append(
                dict(center=mid, axis=axis, d=2 * a["r"], depth=dist,
                     kind=kind, extent="through")
            )
        else:
            used.add(i)
            kind, direction = classify(mesh, a["center"], a["normal"], a["r"])
            depth = probe_depth(mesh, a["center"], direction) if kind == "hole" else None
            features.append(
                dict(center=a["center"], axis=direction, d=2 * a["r"],
                     depth=depth, kind=kind, extent="blind")
            )

    out = []
    for f in features:
        matches = sorted(
            (h for h in HARDWARE if 0 <= f["d"] - h["d"] <= MATCH_TOL
             or abs(f["d"] - h["d"]) <= 0.15),
            key=lambda h: abs(f["d"] - h["d"]),
        )
        c, ax = f["center"], f["axis"]
        protect = "{}:{:.3f},{:.3f},{:.3f},{:.4f},{:.4f},{:.4f},{:.3f},{}".format(
            "cyl" if f["kind"] == "hole" else "boss",
            c[0], c[1], c[2], ax[0], ax[1], ax[2], f["d"],
            f"{f['depth']:.3f},{f['extent']}" if f["depth"] else f"0,{f['extent']}",
        )
        out.append({
            "kind": f["kind"],
            "extent": f["extent"],
            "diameter_mm": round(f["d"], 3),
            "depth_mm": round(f["depth"], 3) if f["depth"] else None,
            "center": [round(float(x), 3) for x in c],
            "axis": [round(float(x), 4) for x in ax],
            "hardware_candidates": [
                {"name": m["name"], "nominal_d": m["d"],
                 "clearance_mm": round(f["d"] - m["d"], 3)}
                for m in matches[:3]
            ],
            "protect_arg": protect,
        })

    print(json.dumps(out, indent=2))
    if not out:
        print("No cylindrical features detected. Low-poly/organic mesh? "
              "Measure manually with cross-sections.", file=sys.stderr)


if __name__ == "__main__":
    main()
