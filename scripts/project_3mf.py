#!/usr/bin/env python3
"""Add geometry to an existing Bambu Studio project 3MF without losing anything.

Bambu Studio project helper for Jeff's A1, A1 mini, and X1 Carbon. It is not
the Snapmaker U1 path and not the Kobra X path, and a Bambu printer tool is
not required before using it. Do not invent a machine profile. Add geometry to
his own project file when he already has one -- it carries his printer,
filament, and process settings, so he opens it and hits Slice. A live Bambu
tool may slice those three machines; it must not be guessed onto a U1 or Kobra.

Two operations, both preserving every other zip entry byte-for-byte, including
per-triangle paint on untouched objects:

    # fuse a new body into an existing object (becomes a "part" of it)
    python project_3mf.py add-part --project p.3mf --object 8 \
        --mesh baseplate.stl --print-scale --name "Gridfinity floor" --out p.3mf

    # add a whole new plate holding one or more meshes
    python project_3mf.py add-plate --project p.3mf \
        --mesh bin_a.stl bin_b.stl --extruder 6 --name "Bins" --out p.3mf

    python project_3mf.py inspect --project p.3mf

WHY add-part instead of a boolean union: Bambu paint data is per-triangle and
positional. A boolean rewrites the triangle list and silently destroys it. A
second part in the same object is fused by the slicer anyway, so the printed
result is identical while the original mesh -- and its paint -- is untouched.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
NS = "{%s}" % CORE
MODEL = "3D/3dmodel.model"
RELS = "3D/_rels/3dmodel.model.rels"
MSET = "Metadata/model_settings.config"
PSET = "Metadata/project_settings.config"
# Bambu lays plates out on an infinite sheet, 3 per row, striding bed_size*1.2.
# Verified against a 6-plate H2C project: x 396.0 = 330*1.2, y 384.0 = 320*1.2.
PLATE_STRIDE_FACTOR = 1.2
PLATES_PER_ROW = 3


def read_zip(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}, list(z.namelist())


def write_zip(path, blobs, order):
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for n in order:
            z.writestr(n, blobs[n])
        for n in blobs:
            if n not in order:
                z.writestr(n, blobs[n])
    os.replace(tmp, path)


def bed_size(blobs):
    try:
        cfg = json.loads(blobs[PSET])
        pts = [p.split("x") for p in cfg["printable_area"]]
        xs = [float(a) for a, _ in pts]
        ys = [float(b) for _, b in pts]
        return max(xs) - min(xs), max(ys) - min(ys)
    except Exception:
        return 256.0, 256.0


def item_matrix(t):
    """12-number 3MF transform -> 4x4. Verified against real Bambu projects."""
    return np.array([[t[0], t[3], t[6], t[9]],
                     [t[1], t[4], t[7], t[10]],
                     [t[2], t[5], t[8], t[11]],
                     [0, 0, 0, 1]])


def mesh_xml(oid, m):
    vs = "\n".join('     <vertex x="%.6f" y="%.6f" z="%.6f"/>' % tuple(v) for v in m.vertices)
    ts = "\n".join('     <triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in m.faces)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<model unit="millimeter" xml:lang="en-US" '
            'xmlns="%s" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
            'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" '
            'requiredextensions="p">\n'
            ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
            ' <resources>\n  <object id="%d" type="model">\n   <mesh>\n'
            '    <vertices>\n%s\n    </vertices>\n'
            '    <triangles>\n%s\n    </triangles>\n'
            '   </mesh>\n  </object>\n </resources>\n <build/>\n</model>\n'
            % (CORE, oid, vs, ts)).encode()


def next_ids(blobs):
    root = ET.fromstring(blobs[MODEL])
    ids = [int(o.get("id")) for o in root.iter(NS + "object")]
    for n in blobs:
        if n.startswith("3D/Objects/"):
            ids += [int(o.get("id")) for o in ET.fromstring(blobs[n]).iter(NS + "object")]
    cfg = blobs[MSET].decode()
    pids = [int(s.split('"')[1]) for s in cfg.split('<part id=')[1:]]
    return max(ids) + 1, max(pids + [0]) + 1


def object_scale(blobs, oid):
    root = ET.fromstring(blobs[MODEL])
    for it in root.iter(NS + "item"):
        if it.get("objectid") == str(oid):
            M = item_matrix([float(x) for x in it.get("transform").split()])
            return float(np.linalg.norm(M[:3, 0]))
    raise SystemExit(f"object {oid} has no <build><item>; is that a top-level object id?")


def load_mesh(p):
    m = trimesh.load(p, force="mesh")
    m.merge_vertices()
    return m


def add_part(args):
    blobs, order = read_zip(args.project)
    mid, pid = next_ids(blobs)
    m = load_mesh(args.mesh)
    if args.print_scale:
        s = object_scale(blobs, args.object)
        m.apply_scale(1.0 / s)
        print(f"  object {args.object} build scale = {s:.6f}; mesh divided by it")
    blobs[f"3D/Objects/object_{mid}.model"] = mesh_xml(mid, m)

    root = blobs[MODEL].decode()
    anchor = f'<object id="{args.object}"'
    if anchor not in root:
        raise SystemExit(f"object id {args.object} not found in {MODEL}")
    head, tail = root.split(anchor, 1)
    close = tail.index("</components>")
    comp = (f'\n    <component p:path="/3D/Objects/object_{mid}.model" '
            f'objectid="{mid}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n   ')
    blobs[MODEL] = (head + anchor + tail[:close] + comp + tail[close:]).encode()

    blobs[RELS] = blobs[RELS].decode().replace(
        "</Relationships>",
        f' <Relationship Target="/3D/Objects/object_{mid}.model" Id="rel-{mid}" '
        f'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n'
        "</Relationships>").encode()

    cfg = blobs[MSET].decode()
    key = f'<object id="{args.object}">'
    if key not in cfg:
        raise SystemExit(f"object {args.object} not in {MSET}")
    h, t = cfg.split(key, 1)
    end = t.index("</object>")
    part = (f'    <part id="{pid}" subtype="normal_part">\n'
            f'      <metadata key="name" value="{args.name}"/>\n'
            f'      <metadata key="matrix" value="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
            f'      <mesh_stat face_count="{len(m.faces)}" edges_fixed="0" '
            f'degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>\n'
            f'    </part>\n')
    blobs[MSET] = (h + key + t[:end] + part + t[end:]).encode()

    write_zip(args.out, blobs, order + [f"3D/Objects/object_{mid}.model"])
    print(f"  added part id={pid} (mesh object {mid}, {len(m.faces)} faces) to object {args.object}")
    print(f"  wrote {args.out}")


def shelf_pack(sizes, bed, margin=15.0, gap=12.0):
    """Left-to-right shelves. Returns centers or None if it does not fit."""
    bw, bd = bed
    out = []
    x = margin
    y = margin
    shelf = 0.0
    for w, d in sizes:
        if x + w > bw - margin:
            x = margin
            y += shelf + gap
            shelf = 0.0
        if y + d > bd - margin:
            return None
        out.append((x + w / 2, y + d / 2))
        x += w + gap
        shelf = max(shelf, d)
    return out


def add_plate(args):
    blobs, order = read_zip(args.project)
    bed = bed_size(blobs)
    cfg = blobs[MSET].decode()
    plate_index = cfg.count("<plate>")          # 0-based index of the new plate
    col, row = plate_index % PLATES_PER_ROW, plate_index // PLATES_PER_ROW
    ox = col * bed[0] * PLATE_STRIDE_FACTOR
    oy = -row * bed[1] * PLATE_STRIDE_FACTOR
    print(f"  bed {bed[0]:.0f}x{bed[1]:.0f}  new plate #{plate_index+1} at grid col{col} row{row} "
          f"-> offset ({ox:.1f}, {oy:.1f})")

    meshes = []
    for p in args.mesh:
        m = load_mesh(p)
        b = m.bounds
        m.apply_translation([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
        meshes.append((os.path.splitext(os.path.basename(p))[0], m))
    centers = shelf_pack([(m.extents[0], m.extents[1]) for _, m in meshes], bed)
    if centers is None:
        raise SystemExit("parts do not fit one plate -- split them across two calls")

    mid, pid = next_ids(blobs)
    objs, rels, items, mobjs, insts, newnames = [], [], [], [], [], []
    for (label, m), (lx, ly) in zip(meshes, centers):
        wid, gid = mid, mid + 1          # wrapper object id, mesh object id
        mid += 2
        name = f"3D/Objects/object_{gid}.model"
        blobs[name] = mesh_xml(gid, m)
        newnames.append(name)
        objs.append(f'  <object id="{wid}" type="model">\n   <components>\n'
                    f'    <component p:path="/{name}" objectid="{gid}" '
                    f'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n   </components>\n  </object>')
        rels.append(f' <Relationship Target="/{name}" Id="rel-{gid}" '
                    f'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>')
        items.append(f'  <item objectid="{wid}" transform="1 0 0 0 1 0 0 0 1 '
                     f'{lx+ox:.5f} {ly+oy:.5f} 0" printable="1"/>')
        mobjs.append(f'  <object id="{wid}">\n'
                     f'    <metadata key="name" value="{label}"/>\n'
                     f'    <metadata key="extruder" value="{args.extruder}"/>\n'
                     f'    <part id="{pid}" subtype="normal_part">\n'
                     f'      <metadata key="name" value="{label}"/>\n'
                     f'      <metadata key="matrix" value="1 0 0 0 1 0 0 0 1 0 0 0"/>\n'
                     f'      <mesh_stat face_count="{len(m.faces)}" edges_fixed="0" '
                     f'degenerate_facets="0" facets_removed="0" facets_reversed="0" '
                     f'backwards_edges="0"/>\n    </part>\n  </object>')
        insts.append(f'    <model_instance>\n'
                     f'      <metadata key="object_id" value="{wid}"/>\n'
                     f'      <metadata key="instance_id" value="0"/>\n    </model_instance>')
        pid += 1
        print(f"    {label:22} {m.extents[0]:6.1f}x{m.extents[1]:6.1f}x{m.extents[2]:6.1f} "
              f"@ bed ({lx:6.1f},{ly:6.1f})")

    s = blobs[MODEL].decode()
    s = s.replace(" </resources>", "\n".join(objs) + "\n </resources>")
    s = s.replace(" </build>", "\n".join(items) + "\n </build>")
    blobs[MODEL] = s.encode()
    blobs[RELS] = blobs[RELS].decode().replace(
        "</Relationships>", "\n".join(rels) + "\n</Relationships>").encode()

    plate = ("  <plate>\n"
             f'    <metadata key="plater_id" value="{plate_index+1}"/>\n'
             f'    <metadata key="plater_name" value="{args.name}"/>\n'
             '    <metadata key="locked" value="false"/>\n'
             + "\n".join(insts) + "\n  </plate>\n")
    cfg = cfg.replace("  <plate>", "\n".join(mobjs) + "\n  <plate>", 1)
    if "<assemble>" in cfg:
        cfg = cfg.replace("  <assemble>", plate + "  <assemble>", 1)
    else:
        cfg = cfg.replace("</config>", plate + "</config>")
    blobs[MSET] = cfg.encode()

    write_zip(args.out, blobs, order + newnames)
    print(f"  wrote {args.out}")


def inspect(args):
    blobs, _ = read_zip(args.project)
    cfg = blobs[MSET].decode() if MSET in blobs else ""
    bed = bed_size(blobs)
    print(f"bed {bed[0]:.0f} x {bed[1]:.0f} mm   plate stride "
          f"{bed[0]*PLATE_STRIDE_FACTOR:.0f} x {bed[1]*PLATE_STRIDE_FACTOR:.0f}")
    print(f"plates: {cfg.count('<plate>')}   objects: {cfg.count('<object id=')}   "
          f"parts: {cfg.count('<part id=')}")
    for n in sorted(b for b in blobs if b.startswith("3D/Objects/")):
        d = blobs[n]
        root = ET.fromstring(d)
        o = root.find(f".//{NS}object")
        m = o.find(NS + "mesh")
        nv = len(m.find(NS + "vertices"))
        nt = len(m.find(NS + "triangles"))
        paint = d.count(b"paint_color")
        print(f"  {n:34} id={o.get('id'):>3} v={nv:>6} t={nt:>6} "
              f"painted={paint if paint else '-'}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add-part")
    a.add_argument("--project", required=True)
    a.add_argument("--object", type=int, required=True)
    a.add_argument("--mesh", required=True)
    a.add_argument("--name", default="added part")
    a.add_argument("--print-scale", action="store_true",
                   help="mesh is in print-scale mm; divide by the object's build scale")
    a.add_argument("--out", required=True)
    b = sub.add_parser("add-plate")
    b.add_argument("--project", required=True)
    b.add_argument("--mesh", nargs="+", required=True)
    b.add_argument("--extruder", default="1")
    b.add_argument("--name", default="")
    b.add_argument("--out", required=True)
    c = sub.add_parser("inspect")
    c.add_argument("--project", required=True)
    args = ap.parse_args()

    if args.cmd != "inspect" and os.path.abspath(args.project) != os.path.abspath(args.out):
        shutil.copyfile(args.project, args.out)
        args.project = args.out
    {"add-part": add_part, "add-plate": add_plate, "inspect": inspect}[args.cmd](args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
