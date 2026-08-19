# build123d and the visual render loop

Parametric CAD in code, with an optional local render server that gives you eyes
— send modeling code, get back a PNG, look at it, iterate — instead of reasoning
about geometry blind.

**First, check whether this is the right tool.** For a multi-part assembly whose
parts must fit each other — hinges, snap-fits, sliders, lids, anything with a
moving DOF — hand off to the `cad-khana` skill instead. It wraps build123d with
interference and clearance *assertions* that re-derive from geometry on every
run, plus per-part min-wall and overhang checks. Renders tell you a part looks
right; assertions tell you it fits. Use this file for single parts and for
geometry with no fit relationship to assert.

## The server is original code, bundled with this skill

`server/server.py` is a small FastAPI server written from scratch for this skill
(FastAPI + build123d + trimesh + matplotlib — no VTK, no third-party image to
vet). Earlier versions of the `cad-agent` skill pointed at a third-party Docker
repo; this replaces it with equivalent API shape. Because it is original code,
it can be built and run directly when the user asks — but it should not be
started silently: tell the user a local server is now listening on port 8123.

## Setup (one time)

From the `server/` directory bundled with this skill:

```bash
# Option A: no Docker, just Python
chmod +x run_local.sh && ./run_local.sh

# Option B: Docker, survives reboots
docker compose up -d --build
```

Confirm it is up:

```bash
curl http://localhost:8123/health   # {"status":"ok"}
```

If neither Python nor Docker is available, say so and offer to help install one
rather than silently failing.

**Tell the user before starting it.** This server runs whatever build123d code
is POSTed to it, with no sandbox — that is the feature, not an oversight. Both
launch paths bind it to loopback only (the Docker one via the `127.0.0.1:`
prefix on the port mapping, which must not be removed). It also restarts on
boot under Docker until explicitly stopped. None of that is a reason to avoid
it; it is a reason not to start it silently in the background. build123d also works fine headless without the
server — `scripts/preflight.py` reports where it lives, which is often
`server/.venv/bin/python3` rather than system python.

## Workflow

1. **Create** — POST build123d code to `/model/create` (code must assign
   `result`).
2. **Render** — POST to `/render/3d` or `/render/multiview`, save the PNG, and
   look at it. Does it match the spec or reference photo? If not, it is not done.
3. **Iterate** — POST a fix to `/model/modify`, re-render, look again. Repeat
   until it is a precise match, not just close.
4. **Export** — POST to `/export` for STL/STEP/3MF once it is right.

```bash
# Create
curl -X POST http://localhost:8123/model/create \
  -H "Content-Type: application/json" \
  -d '{"name": "my_part", "code": "from build123d import *\nresult = Box(60, 40, 30)"}'

# Render (multi-view or single iso)
curl -X POST http://localhost:8123/render/multiview -d '{"model_name": "my_part"}' -o views.png
curl -X POST http://localhost:8123/render/3d -d '{"model_name": "my_part", "view": "isometric"}' -o iso.png

# Modify
curl -X POST http://localhost:8123/model/modify \
  -d '{"name": "my_part", "code": "result = result - Pos(20,10,0) * Cylinder(5, 50)"}'

# Export
curl -X POST http://localhost:8123/export -d '{"model_name": "my_part", "format": "stl"}' -o part.stl
```

## Endpoints

| Endpoint | What it does |
|---|---|
| `GET /health` | Liveness check |
| `POST /model/create` | Run build123d code, create model (code must assign `result`) |
| `POST /model/modify` | Modify existing model (`result` pre-loaded with current shape) |
| `GET /model/list` | List models in session |
| `GET /model/{name}/measure` | Bounding box + volume |
| `GET /model/{name}/dimensions` | Same as `measure` — this server doesn't track parametric build variables |
| `POST /render/3d` | 3D flat-shaded render (matplotlib, not VTK) |
| `POST /render/multiview` | 4-view composite (front/top/right/isometric) |
| `POST /render/2d` | Simplified 2D wireframe projection |
| `POST /render/blueprint` | White-on-blue styled version of `/render/2d` |
| `POST /export` | Export STL/STEP/3MF |
| `POST /analyze/printability` | Manifold/watertight/winding check via trimesh |

Not implemented: `/ai/feedback` (needs an LLM API key wired in) and OpenSCAD
interop (`/load_scad`, `/render_scad`, `/convert_scad` — needs the `openscad`
binary). Say so if asked rather than guessing at a response.

## Cheatsheet

```python
from build123d import *

# Primitives
Box(width, depth, height)
Cylinder(radius, height)
Sphere(radius)

# Boolean
a + b   # union
a - b   # subtract
a & b   # intersect

# Position
Pos(x, y, z) * part
part.rotate(Axis.Z, 45)

# Edges
fillet(part.edges(), radius)
chamfer(part.edges(), length)
```

## Principles

- **Renders are your eyes, not your evidence.** Request a render after every
  change so you are not modeling blind — but matplotlib z-sorts imperfectly, so
  confirm anything suspicious with a cross-section and `is_watertight` /
  `body_count` before believing it. A base that looks detached in a render is
  usually a depth-sort artifact.
- **Don't bypass the server** when it is running. Drive changes through
  `/model/modify` so the session state stays coherent.
- **Iterate to match spec, not to "close enough."** Keep rendering and adjusting
  until the part matches the requested dimensions and any reference photo
  precisely.
- Print-oriented constants still apply: wall ≥1.2 mm, 0.2 mm friction-fit
  clearance, and hardware interfaces preserved at measured size.
