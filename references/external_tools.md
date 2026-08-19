# Optional external tool paths

Everything in this file needs a liveness check before you promise it.
`scripts/preflight.py` detects the local binaries and the wrapper CLI; MCP
connectors it cannot see — that is a `ListConnectors` check.

**One entry here is not optional-tier at all.** When the `Bambu_Printer` MCP is
live it is the *primary* print path — see its section at the bottom, and
`printer_control.md` in full. The rest (OrcaSlicer CLI, OpenSCAD MCP) are
genuine fallbacks: the local Python stack in `scripts/` plus build123d does
every mesh and design job without them, and they are kept here so their details
aren't lost, not because anything needs them.

Rule: check first, promise second. Never tell the user you will slice, or design
in OpenSCAD, before confirming the path exists — `scripts/preflight.py` for
local binaries and the CLI, `ListConnectors` for MCP connectors (preflight does
not test MCPs).

## OrcaSlicer wrapper CLI

A bun/TypeScript wrapper (`cli.ts`) that drives OrcaSlicer with patched Bambu
Studio profiles. Not bundled with this skill; it exists only if the user has it
installed from the old `bambu-slicer` layout.

Preflight looks for it at `$BAMBU_SLICER_CLI_DIR` and requires both `cli.ts` and
an installed `node_modules`. In the old layout the CLI sat at
`$BAMBU_SLICER_SKILL_DIR/scripts/cli`:

```bash
export BAMBU_SLICER_SKILL_DIR="/path/to/skills/bambu-slicer"
export BAMBU_SLICER_CLI_DIR="$BAMBU_SLICER_SKILL_DIR/scripts/cli"
```

If the directory is set but deps are missing:

```bash
cd "$BAMBU_SLICER_CLI_DIR" && bun install
```

Environment variables the CLI reads:

| Variable | Purpose |
| --- | --- |
| `ORCA_CLI_PATH` | OrcaSlicer binary. Default `/Applications/OrcaSlicer.app/Contents/MacOS/OrcaSlicer` |
| `BAMBU_PROFILE_BASE` | Where Bambu Studio profile JSONs live |
| `BAMBU_MACHINE_PROFILE` | Machine profile to slice against |
| `BAMBU_OUTPUT_DIR` | Where generated artifacts go |
| `BAMBU_DEFAULT_FILAMENT` | Fallback filament profile |

Usage:

```bash
bun run "$BAMBU_SLICER_CLI_DIR/cli.ts" --input model.stl   # defaults: 0.20 mm Standard, Bambu PLA Basic
bun run "$BAMBU_SLICER_CLI_DIR/cli.ts" --input model.stl --quality 0.12
bun run "$BAMBU_SLICER_CLI_DIR/cli.ts" --input model.stl --filament "Bambu PETG Basic"
bun run "$BAMBU_SLICER_CLI_DIR/cli.ts" --input "box.stl cylinder.stl hook.stl"
bun run "$BAMBU_SLICER_CLI_DIR/cli.ts" --input "a.stl b.stl" --output combined-plate.3mf
bun run "$BAMBU_SLICER_CLI_DIR/cli.ts" --list-profiles
```

Bambu Studio does not need to be running, but its profile JSONs must exist on
disk — the CLI patches them at slice time, replacing Bambu G-code templates with
OrcaSlicer-compatible ones and resolving `inherits` chains inline so OrcaSlicer
can read the profile out-of-tree.

Why OrcaSlicer rather than Bambu Studio's own CLI: Bambu Studio CLI has a known
segfault with P2S 0.4 mm nozzle profiles
([OrcaSlicer #9636](https://github.com/SoftFever/OrcaSlicer/issues/9636)).

Output goes to a generated-artifact temp directory by default. Set
`BAMBU_OUTPUT_DIR` when the user picks somewhere else. Never write generated
3MF/G-code into `~/Downloads` unless they ask for a one-off there.

**Even with the CLI live, `--list-profiles` must show a real profile for the
user's printer.** A binary with no H2 profile is worse than no binary — it
invites fabricating one. See `print_prep.md`.

## OpenSCAD MCP

Only if `ListConnectors` shows the `openscad` MCP live. preflight's `openscad`
row reports a local binary, which is a different thing and does not authorise
this path. build123d is the default and needs no connector.

Best for functional/geometric parts; unsuited to organic shapes (use MakerWorld).

1. Establish dimensions and constraints from the description or photo.
2. `create_scad_script` — write the OpenSCAD source.
3. `render_preview` — show the user for approval.
4. Iterate on feedback.
5. `export_stl`.
6. Hand off to print prep.

Design tips carried over: `$fn = 64` or higher for smooth curves, 0.2 mm
tolerance on friction fits, wall minimum 1.2 mm (3 perimeters at 0.4 mm),
gridfinity 42 mm grid with 7 mm base height. Always pin down dimensions — a part
that does not fit is useless.

## Browser automation

MakerWorld browsing needs `claude-in-chrome` or an equivalent agent-browser. See
`makerworld.md`.

## Bambu_Printer MCP

Not optional-tier at all when it is live — it slices with a real `h2c` machine
profile, drives the printer, and reports live AMS inventory, which makes it the
primary print path rather than a fallback. `printer_control.md` covers it in
full. It is listed here only because it is still an MCP connector, so it needs a
`ListConnectors` check before you promise anything that depends on it.
