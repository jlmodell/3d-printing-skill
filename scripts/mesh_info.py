#!/usr/bin/env python3
"""Inspect an STL/3MF file: dimensions, integrity, objects, colors.

Usage: python mesh_info.py <file.stl|file.3mf>
"""
import json
import sys
import zipfile

import numpy as np
import trimesh


def summarize_mesh(m, name="mesh"):
    ext = m.bounds
    return {
        "name": name,
        "dimensions_mm": [round(float(x), 3) for x in (ext[1] - ext[0])],
        "bounds_min": [round(float(x), 3) for x in ext[0]],
        "bounds_max": [round(float(x), 3) for x in ext[1]],
        "triangles": int(len(m.faces)),
        "vertices": int(len(m.vertices)),
        "watertight": bool(m.is_watertight),
        "winding_consistent": bool(m.is_winding_consistent),
        "volume_mm3": round(float(m.volume), 2) if m.is_watertight else None,
        "has_vertex_colors": bool(
            m.visual.kind == "vertex" if m.visual is not None else False
        ),
        "has_face_colors": bool(
            m.visual.kind == "face" if m.visual is not None else False
        ),
    }


def inspect_3mf_container(path):
    """Peek inside the 3MF zip for Bambu-specific payloads."""
    info = {"is_bambu_project": False, "entries": [], "painted": False}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        info["entries"] = names
        info["is_bambu_project"] = any(n.startswith("Metadata/") for n in names)
        for n in names:
            if n.endswith(".model"):
                data = z.read(n)
                if b"paint_color" in data or b"mmu_segmentation" in data:
                    info["painted"] = True
    return info


def main():
    path = sys.argv[1]
    out = {"file": path}

    if path.lower().endswith(".3mf"):
        out["container"] = inspect_3mf_container(path)

    scene_or_mesh = trimesh.load(path)
    if isinstance(scene_or_mesh, trimesh.Scene):
        out["type"] = "scene"
        out["objects"] = [
            summarize_mesh(g, name) for name, g in scene_or_mesh.geometry.items()
        ]
        ext = scene_or_mesh.bounds
        out["overall_dimensions_mm"] = [
            round(float(x), 3) for x in (ext[1] - ext[0])
        ]
    else:
        out["type"] = "mesh"
        out["objects"] = [summarize_mesh(scene_or_mesh)]
        out["overall_dimensions_mm"] = out["objects"][0]["dimensions_mm"]

    # H2C build volume check (left-nozzle-only envelope)
    dims = sorted(out["overall_dimensions_mm"], reverse=True)
    h2c = sorted([325, 320, 325], reverse=True)
    out["fits_h2c_single_nozzle"] = all(d <= v for d, v in zip(dims, h2c))
    out["fits_h2c_dual_nozzle"] = all(
        d <= v for d, v in zip(dims, sorted([300, 320, 325], reverse=True))
    )

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
