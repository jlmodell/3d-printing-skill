#!/usr/bin/env python3
"""Environment preflight for the 3d-printing skill.

Run this FIRST, every time the skill runs, before promising the user anything.
It reports which capabilities are live and which fallback to use for the rest.

    python scripts/preflight.py            # human-readable
    python scripts/preflight.py --json     # machine-readable

Exit code is always 0 -- a missing capability is information, not an error.
The point is to know the fallback before starting, not to abort.
"""
import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys

CAD_SERVER = os.environ.get("CAD_AGENT_URL", "http://localhost:8123")

# module -> what breaks without it
PY_DEPS = {
    "trimesh":    "mesh load/measure/section - core, nothing works without it",
    "numpy":      "core",
    "shapely":    "cavity polygons, rounded-rect profiles, baseplate outlines",
    "manifold3d": "boolean union/difference (smart_scale --mode recut)",
    "rtree":      "trimesh section -> polygons_full (cavity detection)",
    "lxml":       "3MF XML rewriting (bambu_3mf.py)",
    "scipy":      "feature detection clustering",
    "networkx":   "trimesh graph ops",
}


def check_python():
    out = {}
    for mod, why in PY_DEPS.items():
        try:
            importlib.import_module(mod)
            out[mod] = {"ok": True, "why": why}
        except Exception as exc:
            out[mod] = {"ok": False, "why": why, "error": type(exc).__name__}
    return out


def check_cad_server():
    try:
        import urllib.request
        with urllib.request.urlopen(CAD_SERVER + "/health", timeout=3) as r:
            return {"ok": r.status == 200, "url": CAD_SERVER}
    except Exception as exc:
        return {"ok": False, "url": CAD_SERVER, "error": type(exc).__name__}


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_build123d():
    """build123d may live in the bundled render-server venv, not system python."""
    try:
        importlib.import_module("build123d")
        return {"ok": True, "where": "system python"}
    except Exception:
        pass
    for base in (
        SKILL_DIR,
        os.environ.get("CAD_AGENT_SKILL_DIR", ""),
        os.path.expanduser("~/.claude/skills/synced/3d-printing"),
        os.path.expanduser("~/.claude/skills/synced/cad-agent"),
        os.path.expanduser("~/.pi/agent/skills/cad-agent"),
    ):
        if not base:
            continue
        py = os.path.join(base, "server", ".venv", "bin", "python3")
        if os.path.exists(py):
            try:
                subprocess.run([py, "-c", "import build123d"], check=True,
                               capture_output=True, timeout=60)
                return {"ok": True, "where": py}
            except Exception:
                pass
    return {"ok": False, "where": None}


def check_slicer():
    """OrcaSlicer / Bambu Studio presence AND whether an H2 profile exists.

    A slicer binary without a profile for the user's printer is worse than no
    slicer: it invites fabricating a machine profile, which produces
    plausible-looking G-code that can crash a toolhead. Report both.
    """
    binary = None
    for cand in ("orca-slicer", "orcaslicer", "OrcaSlicer", "bambu-studio", "BambuStudio"):
        p = shutil.which(cand)
        if p:
            binary = p
            break
    for cand in ("/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer",
                 "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio",
                 os.environ.get("ORCA_CLI_PATH", "")):
        if cand and os.path.exists(cand):
            binary = binary or cand

    profile_dirs = [
        os.path.expanduser("~/.config/BambuStudio"),
        os.path.expanduser("~/Library/Application Support/BambuStudio"),
        os.path.expanduser("~/.config/OrcaSlicer"),
        os.path.expanduser("~/Library/Application Support/OrcaSlicer"),
    ]
    profiles = [d for d in profile_dirs if os.path.isdir(d)]

    h2 = False
    for d in profiles:
        for root, _dirs, files in os.walk(d):
            if any("H2" in f for f in files):
                h2 = True
                break
            if h2:
                break
    return {"binary": binary, "profile_dirs": profiles, "h2_profile_found": h2,
            "ok": bool(binary) and h2}


def check_optional_externals():
    """Nice-to-have paths that are frequently absent. Never assume; never promise.

    OpenSCAD and the OrcaSlicer wrapper CLI are usable when genuinely present,
    but the local Python stack is the primary path either way. A missing entry
    here changes nothing except what you tell the user you are going to do.
    """
    cli_dir = os.environ.get("BAMBU_SLICER_CLI_DIR", "")
    cli_ok = bool(cli_dir) and os.path.isfile(os.path.join(cli_dir, "cli.ts")) \
        and os.path.isdir(os.path.join(cli_dir, "node_modules"))
    return {
        "openscad_binary": shutil.which("openscad"),
        "orca_cli": {"ok": cli_ok, "dir": cli_dir or None,
                     "bun": shutil.which("bun")},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    report = {
        "python": check_python(),
        "cad_server": check_cad_server(),
        "build123d": check_build123d(),
        "slicer": check_slicer(),
        "optional": check_optional_externals(),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print("3d-printing preflight")
    print("=" * 60)
    missing = [m for m, v in report["python"].items() if not v["ok"]]
    for mod, v in report["python"].items():
        print(f"  [{'ok ' if v['ok'] else 'MISS'}] {mod:12} {v['why']}")
    if missing:
        print("\n  fix: pip install " + " ".join(missing) + " --break-system-packages")

    cs = report["cad_server"]
    print(f"\n  [{'ok ' if cs['ok'] else 'down'}] render server        @ {cs['url']}")
    if not cs["ok"]:
        print("       start: server/run_local.sh (bundled with this skill)  (needed only for visual CAD iteration)")

    b = report["build123d"]
    print(f"  [{'ok ' if b['ok'] else 'MISS'}] build123d ({b['where'] or 'not found'})")

    s = report["slicer"]
    print(f"  [{'ok ' if s['ok'] else 'MISS'}] slicer: binary={s['binary'] or 'none'} "
          f"H2-profile={'yes' if s['h2_profile_found'] else 'NO'}")

    o = report["optional"]
    print(f"  [{'ok ' if o['openscad_binary'] else '--  '}] openscad binary: {o['openscad_binary'] or 'absent (fine — build123d is primary)'}")
    print(f"  [{'ok ' if o['orca_cli']['ok'] else '--  '}] OrcaSlicer wrapper CLI: "
          f"{o['orca_cli']['dir'] or 'absent (fine — emit a project 3MF)'}")

    print("\nCAPABILITY / FALLBACK")
    print("-" * 60)
    print(f"  parametric design : {'build123d' if b['ok'] else 'shapely+trimesh profiles (scripts/gridfinity_gen.py)'}")
    print(f"  visual iteration  : {'bundled render server' if cs['ok'] else 'matplotlib Poly3DCollection + numeric cross-sections'}")
    print( "  design authority  : NEVER OpenSCAD MCP unless ListConnectors shows it live")
    if s["ok"]:
        print("  print output      : slice locally with the detected profile")
    else:
        print("  print output      : NO LOCAL SLICER. Do not require a Bambu printer tool.")
        print("                      Hand back the file from SKILL.md Your setup:")
        print("                      Bambu 3MF for A1, A1 mini, X1 Carbon;")
        print("                      Orca-style 3MF with filament slots for the Snapmaker U1;")
        print("                      STL for the Anycubic Kobra X.")
        print("                      Never fabricate a machine profile.")
        print("                      A live Bambu tool is optional, and only for the Bambu")
        print("                      machines (references/printer_control.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
