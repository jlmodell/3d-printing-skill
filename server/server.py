#!/usr/bin/env python3
"""
cad-server: a small, original, local HTTP API for iterating on build123d
CAD models with visual feedback (create -> render -> look -> iterate -> export).

This is NOT the Svetlana-DAO-LLC/cad-agent project. It is written from
scratch to expose a similar-shaped HTTP API so a coding agent can drive it,
without pulling and running someone else's unvetted Docker image. Every
line here is original and MIT-licensed for your own use.

Run directly:
    pip install -r requirements.txt
    python server.py

Or via Docker:
    docker compose up -d --build

Binds to 127.0.0.1 by default (localhost only). This service executes
arbitrary Python (the build123d code you send it) -- that's the point of
the tool, but it means it should only ever be exposed to localhost/your
own machine, never to the open internet.
"""

import io
import os
import tempfile
import traceback
from typing import Optional

import matplotlib

matplotlib.use("Agg")  # headless, no display server needed
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection  # noqa: E402

import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.responses import Response  # noqa: E402
from pydantic import BaseModel  # noqa: E402

app = FastAPI(title="cad-server", version="1.0.0")

# In-memory model store: name -> {"shape": build123d object, "history": [code, ...]}
MODELS: dict = {}

VIEW_ANGLES = {
    "isometric": (30, 45),
    "front": (0, -90),
    "back": (0, 90),
    "top": (90, -90),
    "bottom": (-90, -90),
    "right": (0, 0),
    "left": (0, 180),
}

PROJECTION_AXES = {
    # view -> (horizontal index, vertical index) into xyz
    "front": (0, 2),
    "top": (0, 1),
    "right": (1, 2),
    "side": (1, 2),
}


# --------------------------------------------------------------------------
# Request models
# --------------------------------------------------------------------------

class CreateModelRequest(BaseModel):
    name: str
    code: str


class ModifyModelRequest(BaseModel):
    name: str
    code: str


class RenderRequest(BaseModel):
    model_name: str
    view: Optional[str] = "isometric"


class ExportRequest(BaseModel):
    model_name: str
    format: str  # stl | step | 3mf


class AnalyzeRequest(BaseModel):
    model_name: str


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def get_model(name: str):
    entry = MODELS.get(name)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"no model named '{name}'")
    return entry["shape"]


def run_build123d_code(code: str, existing_shape=None):
    """Execute build123d code in a fresh namespace and return namespace['result']."""
    import build123d  # local import so the module loads lazily

    namespace = {}
    exec("from build123d import *", namespace)  # noqa: S102
    if existing_shape is not None:
        namespace["result"] = existing_shape
    try:
        exec(code, namespace)  # noqa: S102
    except Exception:
        raise HTTPException(
            status_code=400,
            detail=f"error running code:\n{traceback.format_exc()}",
        )
    if "result" not in namespace:
        raise HTTPException(
            status_code=400,
            detail="code must assign the final shape to a variable named `result`",
        )
    return namespace["result"]


def shape_to_trimesh(shape) -> trimesh.Trimesh:
    from build123d import export_stl

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        path = f.name
    try:
        export_stl(shape, path)
        mesh = trimesh.load_mesh(path, file_type="stl")
    finally:
        os.unlink(path)
    if isinstance(mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(mesh.dump())
    return mesh


def fig_to_png_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf.read()


def draw_solid_view(ax, mesh: trimesh.Trimesh, view: str):
    # Flat-shade each triangle by its face normal so the surface reads as a
    # solid instead of a wireframe of STL triangulation seams.
    light_dir = np.array([0.45, -0.45, 0.77])
    light_dir = light_dir / np.linalg.norm(light_dir)
    normals = mesh.face_normals
    # Round normals before shading so near-coplanar STL triangulation slivers
    # (numerically-noisy normals on a nominally flat face) don't produce a
    # visible moire/banding pattern -- they should all shade identically.
    rounded_normals = np.round(normals, 3)
    intensity = np.clip(rounded_normals @ light_dir, 0.45, 1.0)  # 0.45 = ambient floor
    base_color = np.array([0.66, 0.77, 0.88])
    face_colors = np.clip(base_color[None, :] * intensity[:, None], 0, 1)
    face_colors = np.hstack([face_colors, np.ones((len(face_colors), 1))])

    # antialiased=False avoids matplotlib bleeding faint seam lines along
    # shared polygon boundaries even when edgecolor='none'.
    poly = Poly3DCollection(
        mesh.triangles, facecolors=face_colors, edgecolor="none", antialiased=False
    )
    ax.add_collection3d(poly)

    # Only draw "feature" edges (real geometric edges/corners), not the
    # internal seams from how the mesher triangulated flat faces -- those
    # are what caused the star-shaped artifact around curved cutouts.
    if len(mesh.face_adjacency_angles):
        feature = mesh.face_adjacency_angles > np.radians(12)
        feature_edges = mesh.face_adjacency_edges[feature]
        if len(feature_edges):
            segs = mesh.vertices[feature_edges]
            ax.add_collection3d(Line3DCollection(segs, colors="black", linewidths=0.5))

    bounds = mesh.bounds
    ax.set_xlim(bounds[0][0], bounds[1][0])
    ax.set_ylim(bounds[0][1], bounds[1][1])
    ax.set_zlim(bounds[0][2], bounds[1][2])
    try:
        ax.set_box_aspect(tuple(mesh.extents))
    except Exception:
        pass
    elev, azim = VIEW_ANGLES.get(view, VIEW_ANGLES["isometric"])
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/model/create")
def model_create(req: CreateModelRequest):
    shape = run_build123d_code(req.code)
    MODELS[req.name] = {"shape": shape, "history": [req.code]}
    return {"name": req.name, "status": "created"}


@app.post("/model/modify")
def model_modify(req: ModifyModelRequest):
    entry = MODELS.get(req.name)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"no model named '{req.name}'")
    new_shape = run_build123d_code(req.code, existing_shape=entry["shape"])
    entry["shape"] = new_shape
    entry["history"].append(req.code)
    return {"name": req.name, "status": "modified"}


@app.get("/model/list")
def model_list():
    return {"models": list(MODELS.keys())}


@app.get("/model/{name}/measure")
def model_measure(name: str):
    shape = get_model(name)
    bbox = shape.bounding_box()
    size = (
        bbox.max.X - bbox.min.X,
        bbox.max.Y - bbox.min.Y,
        bbox.max.Z - bbox.min.Z,
    )
    result = {
        "bounding_box_mm": {
            "min": [bbox.min.X, bbox.min.Y, bbox.min.Z],
            "max": [bbox.max.X, bbox.max.Y, bbox.max.Z],
            "size": list(size),
        }
    }
    try:
        result["volume_mm3"] = shape.volume
    except Exception:
        result["volume_mm3"] = None
    return result


@app.get("/model/{name}/dimensions")
def model_dimensions(name: str):
    # Simplified stand-in: this from-scratch server doesn't track parametric
    # build variables, so it reports geometric dimensions instead.
    return model_measure(name)


@app.post("/render/3d")
def render_3d(req: RenderRequest):
    shape = get_model(req.model_name)
    mesh = shape_to_trimesh(shape)
    fig = plt.figure(figsize=(6, 6), dpi=150)
    ax = fig.add_subplot(111, projection="3d")
    draw_solid_view(ax, mesh, req.view or "isometric")
    png = fig_to_png_bytes(fig)
    return Response(content=png, media_type="image/png")


@app.post("/render/multiview")
def render_multiview(req: RenderRequest):
    shape = get_model(req.model_name)
    mesh = shape_to_trimesh(shape)
    fig = plt.figure(figsize=(10, 10), dpi=150)
    for i, view in enumerate(["front", "top", "right", "isometric"]):
        ax = fig.add_subplot(2, 2, i + 1, projection="3d")
        draw_solid_view(ax, mesh, view)
        ax.set_title(view, fontsize=9)
    png = fig_to_png_bytes(fig)
    return Response(content=png, media_type="image/png")


@app.post("/render/2d")
def render_2d(req: RenderRequest):
    shape = get_model(req.model_name)
    mesh = shape_to_trimesh(shape)
    view = req.view or "front"
    i, j = PROJECTION_AXES.get(view, PROJECTION_AXES["front"])
    verts = mesh.vertices[:, [i, j]]
    edges = mesh.edges_unique
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    segs = verts[edges]  # (n_edges, 2, 2)
    for seg in segs:
        ax.plot(seg[:, 0], seg[:, 1], color="black", linewidth=0.4)
    ax.set_aspect("equal")
    ax.axis("off")
    png = fig_to_png_bytes(fig)
    return Response(content=png, media_type="image/png")


@app.post("/render/blueprint")
def render_blueprint(req: RenderRequest):
    shape = get_model(req.model_name)
    mesh = shape_to_trimesh(shape)
    view = req.view or "front"
    i, j = PROJECTION_AXES.get(view, PROJECTION_AXES["front"])
    verts = mesh.vertices[:, [i, j]]
    edges = mesh.edges_unique
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150, facecolor="#1b3a6b")
    ax.set_facecolor("#1b3a6b")
    segs = verts[edges]
    for seg in segs:
        ax.plot(seg[:, 0], seg[:, 1], color="white", linewidth=0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    png = fig_to_png_bytes(fig)
    return Response(content=png, media_type="image/png")


@app.post("/export")
def export_model(req: ExportRequest):
    shape = get_model(req.model_name)
    fmt = req.format.lower()
    with tempfile.NamedTemporaryFile(suffix=f".{fmt}", delete=False) as f:
        path = f.name
    try:
        if fmt == "stl":
            from build123d import export_stl

            export_stl(shape, path)
            media_type = "model/stl"
        elif fmt == "step":
            from build123d import export_step

            export_step(shape, path)
            media_type = "application/step"
        elif fmt == "3mf":
            from build123d import Mesher

            exporter = Mesher()
            exporter.add_shape(shape)
            exporter.write(path)
            media_type = "model/3mf"
        else:
            raise HTTPException(status_code=400, detail=f"unsupported format '{fmt}'")
        with open(path, "rb") as f:
            data = f.read()
    finally:
        if os.path.exists(path):
            os.unlink(path)
    return Response(content=data, media_type=media_type)


@app.post("/analyze/printability")
def analyze_printability(req: AnalyzeRequest):
    shape = get_model(req.model_name)
    mesh = shape_to_trimesh(shape)
    return {
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "volume_mm3": float(mesh.volume) if mesh.is_watertight else None,
        "bounds_mm": mesh.bounds.tolist(),
        "euler_number": int(mesh.euler_number),
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", "8123"))
    host = os.environ.get("HOST", "127.0.0.1")
    uvicorn.run(app, host=host, port=port)
