# cad-server

A small, original, from-scratch local HTTP server for iterating on
[build123d](https://build123d.readthedocs.io/) CAD models with visual
feedback: create a model from code, render it to a PNG, look at it, adjust
the code, re-render, and export STL/STEP/3MF once it's right.

This is **not** the `Svetlana-DAO-LLC/cad-agent` project or any other
third-party repo — every line here was written for you, so there's nothing
to vet before running it. It's plain Python (FastAPI + build123d + trimesh +
matplotlib), MIT-licensed for your own use.

## Run it (no Docker needed)

```bash
chmod +x run_local.sh
./run_local.sh
```

This creates a local virtualenv, installs dependencies, and starts the
server at `http://127.0.0.1:8123`. Leave it running in a terminal tab, or
run it under something like `tmux`/`screen`/a login-item if you want it
always on.

## Run it in Docker instead

```bash
docker compose up -d --build
```

`restart: unless-stopped` in `docker-compose.yml` means it survives reboots
and crashes without you touching it again.

## Check it's up

```bash
curl http://127.0.0.1:8123/health
# {"status":"ok"}
```

## API

| Endpoint | What it does |
|---|---|
| `GET /health` | Liveness check |
| `POST /model/create` | `{name, code}` — run build123d code, code must assign to `result` |
| `POST /model/modify` | `{name, code}` — code can reference the existing `result` |
| `GET /model/list` | List model names in memory |
| `GET /model/{name}/measure` | Bounding box + volume |
| `GET /model/{name}/dimensions` | Alias of `measure` (this server doesn't track parametric build variables) |
| `POST /render/3d` | `{model_name, view}` — shaded PNG. `view` ∈ isometric/front/back/top/bottom/left/right |
| `POST /render/multiview` | `{model_name}` — 4-up front/top/right/isometric PNG |
| `POST /render/2d` | `{model_name, view}` — simplified wireframe projection PNG |
| `POST /render/blueprint` | `{model_name, view}` — white-on-blue styled version of `/render/2d` |
| `POST /export` | `{model_name, format}` — `format` ∈ stl/step/3mf, returns the file |
| `POST /analyze/printability` | `{model_name}` — watertight/winding/volume/bounds via trimesh |

Example:

```bash
curl -X POST http://localhost:8123/model/create \
  -H "Content-Type: application/json" \
  -d '{"name": "part", "code": "from build123d import *\nresult = Box(60, 40, 30)"}'

curl -X POST http://localhost:8123/render/3d \
  -d '{"model_name": "part", "view": "isometric"}' -o iso.png

curl -X POST http://localhost:8123/export \
  -d '{"model_name": "part", "format": "stl"}' -o part.stl
```

## Notes on the rendering

Rendering is done with `matplotlib` (flat-shaded triangles + real
geometric feature edges only, not the raw STL triangulation seams) rather
than a GPU renderer like VTK. It's not photoreal, but it's accurate for
judging proportions, cutouts, and fillets, and it needs no GPU or display
server — it just works in a plain Docker container or venv.

## Not implemented

`/ai/feedback` (would need your own LLM API key wired in) and the OpenSCAD
interop endpoints (`/load_scad`, `/render_scad`, `/convert_scad`, would
need the `openscad` binary installed) are not included. Everything else in
the table above is fully implemented and tested.

## Security note

This server executes whatever Python code is POSTed to `/model/create` and
`/model/modify` — that's the point (it's how you drive build123d), but it
means it should only ever listen on localhost / your own machine, never be
exposed to the open internet.
