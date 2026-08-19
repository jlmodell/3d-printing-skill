#!/usr/bin/env python3
"""
3D print log — record prints and settings, then query the history.

The point is that troubleshooting compounds. A stringing problem you solved
six months ago on PETG at 0.12mm is only useful if you can find what you
changed. This keeps a single JSON file you own, in plain text, that a person
can read without any tooling.

Usage:
    printlog.py add --model "Grille v4" --material "PETG" --result success ...
    printlog.py list [--material PETG] [--result fail] [--limit 20]
    printlog.py show <id>
    printlog.py stats
    printlog.py settings --material PETG --nozzle 0.4   # what worked before
    printlog.py issues --issue stringing                # every time it happened
    printlog.py report -o report.md

Log location defaults to ./print-log.json, override with --log.
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

DEFAULT_LOG = "print-log.json"

RESULTS = ("success", "partial", "fail")

COMMON_ISSUES = [
    "stringing", "warping", "bed-adhesion", "layer-adhesion", "under-extrusion",
    "over-extrusion", "elephant-foot", "z-banding", "ringing", "spaghetti",
    "support-removal", "nozzle-clog", "first-layer", "dimensional-accuracy",
    "color-bleed", "purge-waste", "curling", "delamination", "blobs", "seam",
]


def load(path):
    if not os.path.exists(path):
        return {"prints": [], "version": 1}
    with open(path) as f:
        return json.load(f)


def save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False)
    os.replace(tmp, path)


def next_id(data):
    return max((p["id"] for p in data["prints"]), default=0) + 1


# ---------------------------------------------------------------------- add


def cmd_add(args):
    data = load(args.log)
    entry = {
        "id": next_id(data),
        "date": args.date or datetime.now().strftime("%Y-%m-%d"),
        "model": args.model,
        "source": args.source,
        "printer": args.printer,
        "material": args.material,
        "brand": args.brand,
        "color": args.color,
        "nozzle": args.nozzle,
        "layer_height": args.layer_height,
        "nozzle_temp": args.nozzle_temp,
        "bed_temp": args.bed_temp,
        "speed": args.speed,
        "infill": args.infill,
        "walls": args.walls,
        "supports": args.supports,
        "support_z_gap": args.support_z_gap,
        "adhesion": args.adhesion,
        "dried": args.dried,
        "duration_h": args.duration,
        "filament_g": args.grams,
        "result": args.result,
        "issues": args.issue or [],
        "fix": args.fix,
        "notes": args.notes,
    }
    entry = {k: v for k, v in entry.items() if v is not None and v != []}
    if args.issue:
        entry["issues"] = args.issue
    data["prints"].append(entry)
    save(args.log, data)
    print(f"Logged print #{entry['id']}: {entry.get('model', '(unnamed)')} "
          f"[{entry.get('result', '?')}]")
    unknown = set(args.issue or []) - set(COMMON_ISSUES)
    if unknown:
        print(f"  note: new issue tag(s) {sorted(unknown)} — fine, just keep the "
              f"spelling consistent so searches find them later")


# --------------------------------------------------------------------- list


def matches(p, args):
    if args.material and (p.get("material") or "").upper() != args.material.upper():
        return False
    if args.result and p.get("result") != args.result:
        return False
    if args.printer and (p.get("printer") or "").lower() != args.printer.lower():
        return False
    if args.nozzle and p.get("nozzle") != args.nozzle:
        return False
    if args.issue and not (set(args.issue) & set(p.get("issues", []))):
        return False
    if args.model and args.model.lower() not in (p.get("model") or "").lower():
        return False
    return True


def fmt_row(p):
    mark = {"success": "ok  ", "partial": "part", "fail": "FAIL"}.get(
        p.get("result", ""), "?   "
    )
    bits = [
        f"#{p['id']:<4}",
        p.get("date", "----------"),
        mark,
        (p.get("model") or "")[:34].ljust(34),
        (p.get("material") or "")[:8].ljust(8),
        f"{p.get('layer_height', '')}".ljust(6),
    ]
    line = " ".join(bits)
    if p.get("issues"):
        line += "  " + ",".join(p["issues"])
    return line


def cmd_list(args):
    data = load(args.log)
    rows = [p for p in data["prints"] if matches(p, args)]
    rows.sort(key=lambda p: (p.get("date", ""), p["id"]), reverse=True)
    if args.limit:
        rows = rows[: args.limit]
    if not rows:
        print("No matching prints.")
        return
    print(f"{'ID':<5} {'DATE':<10} {'RES':<4} {'MODEL':<34} {'MATL':<8} {'LAYER':<6}  ISSUES")
    for p in rows:
        print(fmt_row(p))
    print(f"\n{len(rows)} print(s).")


def cmd_show(args):
    data = load(args.log)
    for p in data["prints"]:
        if p["id"] == args.id:
            print(json.dumps(p, indent=2))
            return
    sys.exit(f"No print with id {args.id}")


# -------------------------------------------------------------------- stats


def cmd_stats(args):
    data = load(args.log)
    prints = data["prints"]
    if not prints:
        print("Log is empty.")
        return
    total = len(prints)
    res = Counter(p.get("result", "unknown") for p in prints)
    print(f"Total prints logged: {total}")
    for r in RESULTS:
        if res.get(r):
            print(f"  {r:<8} {res[r]:>4}  ({100*res[r]/total:.0f}%)")
    print()

    by_mat = defaultdict(lambda: Counter())
    for p in prints:
        by_mat[p.get("material", "?")][p.get("result", "unknown")] += 1
    print("By material:")
    for mat, c in sorted(by_mat.items(), key=lambda kv: -sum(kv[1].values())):
        n = sum(c.values())
        ok = c.get("success", 0)
        print(f"  {mat:<10} {n:>3} prints, {100*ok/n:>3.0f}% success")
    print()

    issues = Counter()
    for p in prints:
        issues.update(p.get("issues", []))
    if issues:
        print("Most common issues:")
        for issue, n in issues.most_common(10):
            print(f"  {issue:<22} {n}")
        print()

    grams = sum(p.get("filament_g", 0) or 0 for p in prints)
    hours = sum(p.get("duration_h", 0) or 0 for p in prints)
    if grams:
        print(f"Filament used: {grams:.0f} g ({grams/1000:.2f} kg)")
    if hours:
        print(f"Print time: {hours:.1f} h")


# ----------------------------------------------------------------- settings


def cmd_settings(args):
    """Show the settings that actually worked, so a new print starts from
    evidence rather than from the slicer's defaults."""
    data = load(args.log)
    rows = [
        p for p in data["prints"]
        if p.get("result") == "success" and matches(p, args)
    ]
    if not rows:
        print("No successful prints match that filter yet.")
        near = [p for p in data["prints"] if matches(p, args)]
        if near:
            print(f"({len(near)} non-successful print(s) do match — "
                  f"run `list` with the same filters to see what went wrong.)")
        return

    rows.sort(key=lambda p: (p.get("date", ""), p["id"]), reverse=True)
    fields = [
        ("nozzle", "Nozzle"), ("layer_height", "Layer height"),
        ("nozzle_temp", "Nozzle temp"), ("bed_temp", "Bed temp"),
        ("speed", "Speed"), ("infill", "Infill"), ("walls", "Walls"),
        ("supports", "Supports"), ("support_z_gap", "Support Z gap"),
        ("adhesion", "Adhesion"), ("dried", "Filament dried"),
    ]
    print(f"Settings from {len(rows)} successful print(s):\n")
    for key, label in fields:
        vals = Counter(str(p[key]) for p in rows if p.get(key) is not None)
        if not vals:
            continue
        if len(vals) == 1:
            v, n = vals.most_common(1)[0]
            print(f"  {label:<16} {v}   (consistent across {n})")
        else:
            parts = ", ".join(f"{v} x{n}" for v, n in vals.most_common())
            print(f"  {label:<16} {parts}")
    print(f"\nMost recent success: #{rows[0]['id']} — {rows[0].get('model')} "
          f"({rows[0].get('date')})")
    if rows[0].get("notes"):
        print(f"  notes: {rows[0]['notes']}")


# ------------------------------------------------------------------- issues


def cmd_issues(args):
    """Every occurrence of an issue and what fixed it — the whole reason to
    keep a log."""
    data = load(args.log)
    target = args.issue
    rows = [p for p in data["prints"] if not target or (set(target) & set(p.get("issues", [])))]
    if not rows:
        print("No prints logged with that issue.")
        return
    rows.sort(key=lambda p: (p.get("date", ""), p["id"]))
    for p in rows:
        print(f"#{p['id']} {p.get('date')} — {p.get('model')} "
              f"[{p.get('material')}, {p.get('layer_height')}mm, "
              f"{p.get('nozzle')}mm nozzle] → {p.get('result')}")
        print(f"    issues: {', '.join(p.get('issues', []))}")
        if p.get("fix"):
            print(f"    FIX: {p['fix']}")
        if p.get("notes"):
            print(f"    notes: {p['notes']}")
        print()

    fixes = [p["fix"] for p in rows if p.get("fix")]
    if fixes:
        print(f"{len(fixes)} recorded fix(es) above. Start with the most recent one "
              f"that matched your material and nozzle.")


# ------------------------------------------------------------------- report


def cmd_report(args):
    data = load(args.log)
    prints = sorted(data["prints"], key=lambda p: (p.get("date", ""), p["id"]),
                    reverse=True)
    out = ["# Print log", ""]
    if not prints:
        out.append("_No prints logged yet._")
    else:
        total = len(prints)
        ok = sum(1 for p in prints if p.get("result") == "success")
        out.append(f"**{total} prints logged · {100*ok/total:.0f}% success rate**")
        out.append("")
        out.append("| # | Date | Model | Material | Layer | Nozzle | Result | Issues |")
        out.append("|---|---|---|---|---|---|---|---|")
        for p in prints:
            out.append(
                f"| {p['id']} | {p.get('date','')} | {p.get('model','')} | "
                f"{p.get('material','')} | {p.get('layer_height','')} | "
                f"{p.get('nozzle','')} | {p.get('result','')} | "
                f"{', '.join(p.get('issues', []))} |"
            )
        out.append("")
        fixed = [p for p in prints if p.get("fix")]
        if fixed:
            out.append("## Fixes that worked")
            out.append("")
            for p in fixed:
                out.append(f"- **{p.get('material')} / {p.get('layer_height')}mm** — "
                           f"{', '.join(p.get('issues', []))}: {p['fix']} "
                           f"(#{p['id']}, {p.get('date')})")
            out.append("")
    text = "\n".join(out)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
        print(f"Wrote {args.out}")
    else:
        print(text)


# --------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", default=DEFAULT_LOG)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="log a print")
    a.add_argument("--model")
    a.add_argument("--source", help="where the model came from")
    a.add_argument("--date")
    a.add_argument("--printer")
    a.add_argument("--material")
    a.add_argument("--brand")
    a.add_argument("--color")
    a.add_argument("--nozzle", type=float)
    a.add_argument("--layer-height", type=float, dest="layer_height")
    a.add_argument("--nozzle-temp", type=int, dest="nozzle_temp")
    a.add_argument("--bed-temp", type=int, dest="bed_temp")
    a.add_argument("--speed", type=int)
    a.add_argument("--infill")
    a.add_argument("--walls", type=int)
    a.add_argument("--supports")
    a.add_argument("--support-z-gap", type=float, dest="support_z_gap")
    a.add_argument("--adhesion", help="brim, raft, glue, none")
    a.add_argument("--dried", help="yes/no/hours")
    a.add_argument("--duration", type=float, help="hours")
    a.add_argument("--grams", type=float)
    a.add_argument("--result", choices=RESULTS, required=True)
    a.add_argument("--issue", action="append")
    a.add_argument("--fix", help="what solved it")
    a.add_argument("--notes")
    a.set_defaults(func=cmd_add)

    for name, fn, helptext in (
        ("list", cmd_list, "list prints"),
        ("settings", cmd_settings, "settings that worked"),
        ("issues", cmd_issues, "history of an issue"),
    ):
        p = sub.add_parser(name, help=helptext)
        p.add_argument("--material")
        p.add_argument("--result", choices=RESULTS)
        p.add_argument("--printer")
        p.add_argument("--nozzle", type=float)
        p.add_argument("--model")
        p.add_argument("--issue", action="append")
        p.add_argument("--limit", type=int, default=0)
        p.set_defaults(func=fn)

    p = sub.add_parser("show", help="full record")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("stats", help="summary")
    p.set_defaults(func=cmd_stats)

    p = sub.add_parser("report", help="markdown report")
    p.add_argument("-o", "--out")
    p.set_defaults(func=cmd_report)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
