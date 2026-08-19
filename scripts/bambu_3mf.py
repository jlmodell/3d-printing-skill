#!/usr/bin/env python3
"""3MF utilities that respect Bambu Studio project files.

Commands:
  inspect <in.3mf>
      List container entries, objects, materials, paint status.

  transform <in.3mf> <out.3mf> --scale 1.5 [--object-id N]
      Scale vertex coordinates IN PLACE inside the 3MF XML. Every other byte
      of the container (paint data, plate settings, Metadata/) is preserved,
      so Bambu Studio paint and project settings survive. Topology unchanged.

  set-color <in.3mf> <out.3mf> --object-id N --color "#RRGGBB"
      Assign a base material color to an object (becomes a filament slot when
      opened in Bambu Studio).

Namespaces: 3MF core is
http://schemas.microsoft.com/3dmanufacturing/core/2015/02
"""
import argparse
import shutil
import sys
import zipfile

from lxml import etree

NS = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
CORE = NS["m"]


def find_model_entries(z):
    return [n for n in z.namelist() if n.endswith(".model")]


def rewrite_3mf(src, dst, replacements):
    """Copy a 3MF zip, swapping the bytes of entries named in replacements."""
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(
        dst, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for item in zin.infolist():
            data = replacements.get(item.filename, zin.read(item.filename))
            zout.writestr(item, data)


def cmd_inspect(args):
    with zipfile.ZipFile(args.input) as z:
        print("entries:")
        for n in z.namelist():
            print(f"  {n} ({z.getinfo(n).file_size} bytes)")
        for name in find_model_entries(z):
            root = etree.fromstring(z.read(name))
            print(f"\nmodel file: {name}")
            print(f"  unit: {root.get('unit', 'millimeter')}")
            for obj in root.iter(f"{{{CORE}}}object"):
                mesh = obj.find(f"{{{CORE}}}mesh")
                nverts = len(mesh.find(f"{{{CORE}}}vertices")) if mesh is not None else 0
                tris = mesh.find(f"{{{CORE}}}triangles") if mesh is not None else None
                painted = tris is not None and any(
                    "paint_color" in t.attrib or "mmu_segmentation" in t.attrib
                    for t in tris[:200]
                )
                print(f"  object id={obj.get('id')} type={obj.get('type','model')} "
                      f"name={obj.get('name','')} vertices={nverts} "
                      f"painted={'yes' if painted else 'no'}")
            for bm in root.iter(f"{{{CORE}}}basematerials"):
                for base in bm:
                    print(f"  material: {base.get('name')} {base.get('displaycolor')}")


def cmd_transform(args):
    replacements = {}
    with zipfile.ZipFile(args.input) as z:
        for name in find_model_entries(z):
            root = etree.fromstring(z.read(name))
            changed = False
            for obj in root.iter(f"{{{CORE}}}object"):
                if args.object_id and obj.get("id") != str(args.object_id):
                    continue
                mesh = obj.find(f"{{{CORE}}}mesh")
                if mesh is None:
                    continue
                verts = mesh.find(f"{{{CORE}}}vertices")
                # scale about the object's own centroid to keep plate placement
                xs = [float(v.get("x")) for v in verts]
                ys = [float(v.get("y")) for v in verts]
                zs = [float(v.get("z")) for v in verts]
                cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
                cz = min(zs)  # keep model sitting on the plate
                s = args.scale
                for v in verts:
                    v.set("x", f"{(float(v.get('x')) - cx) * s + cx:.6f}")
                    v.set("y", f"{(float(v.get('y')) - cy) * s + cy:.6f}")
                    v.set("z", f"{(float(v.get('z')) - cz) * s + cz:.6f}")
                changed = True
            if changed:
                replacements[name] = etree.tostring(
                    root, xml_declaration=True, encoding="UTF-8")
    if not replacements:
        sys.exit("No matching object found to transform.")
    rewrite_3mf(args.input, args.output, replacements)
    print(f"Scaled by {args.scale} -> {args.output} (paint/metadata preserved)")


def cmd_set_color(args):
    replacements = {}
    with zipfile.ZipFile(args.input) as z:
        for name in find_model_entries(z):
            root = etree.fromstring(z.read(name))
            resources = root.find(f"{{{CORE}}}resources")
            if resources is None:
                continue
            target = None
            for obj in resources.iter(f"{{{CORE}}}object"):
                if obj.get("id") == str(args.object_id):
                    target = obj
                    break
            if target is None:
                continue
            # find or create a basematerials group
            bm = resources.find(f"{{{CORE}}}basematerials")
            if bm is None:
                bm = etree.SubElement(resources, f"{{{CORE}}}basematerials")
                # unique resource id
                ids = {int(o.get("id")) for o in resources if o.get("id")}
                bm.set("id", str(max(ids) + 1 if ids else 100))
                resources.insert(0, bm)
            base = etree.SubElement(bm, f"{{{CORE}}}base")
            base.set("name", args.name or f"Color {args.color}")
            base.set("displaycolor", args.color.upper() + "FF"
                     if len(args.color) == 7 else args.color)
            idx = len(bm) - 1
            target.set("pid", bm.get("id"))
            target.set("pindex", str(idx))
            replacements[name] = etree.tostring(
                root, xml_declaration=True, encoding="UTF-8")
    if not replacements:
        sys.exit(f"Object id {args.object_id} not found.")
    rewrite_3mf(args.input, args.output, replacements)
    print(f"Object {args.object_id} -> {args.color} in {args.output}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("inspect")
    p.add_argument("input")
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("transform")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--scale", type=float, required=True)
    p.add_argument("--object-id", type=int, default=None)
    p.set_defaults(func=cmd_transform)

    p = sub.add_parser("set-color")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--object-id", type=int, required=True)
    p.add_argument("--color", required=True, help="#RRGGBB")
    p.add_argument("--name", default=None)
    p.set_defaults(func=cmd_set_color)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
