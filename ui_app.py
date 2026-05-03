from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request, send_file

from umlement_runner import run_umlement

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
DEFAULT_PATH = str(BASE_DIR / "demo")
SAMPLE_PROJECTS = [
    {"label": "Fantasy gear demo", "path": str(BASE_DIR / "demo")},
    {"label": "Space cafe demo", "path": str(BASE_DIR / "demo_space_cafe")},
    {"label": "Mech pet demo", "path": str(BASE_DIR / "demo_mech_pet")},
]

app = Flask(__name__)


@app.get("/")
def index() -> str:
    return render_template("index.html", default_path=DEFAULT_PATH, sample_projects=SAMPLE_PROJECTS)


@app.post("/api/run")
def run() -> Any:
    payload = request.get_json(silent=True) or {}
    raw_path = str(payload.get("path") or DEFAULT_PATH)
    extra_paths = [str(item) for item in payload.get("extraPaths", []) if str(item).strip()]
    recursive = bool(payload.get("recursive", True))
    output_format = str(payload.get("format") or "svg")
    model_only = bool(payload.get("modelOnly", False))

    progress_lines: list[dict[str, str | None]] = []
    resolved_paths = [raw_path, *extra_paths]

    def capture(label: str, detail: str | None = None) -> None:
        progress_lines.append({"label": label, "detail": detail})

    result = run_umlement(
        [raw_path, *extra_paths],
        recursive=recursive,
        output_format=output_format,
        model_only=model_only,
        progress_callback=capture,
    )

    diagram_url = None
    model_url = None

    if result.diagram_path:
        diagram_url = "/artifacts/umlement.svg" if result.diagram_path.endswith(".svg") else "/artifacts/umlement.png"
    if result.model_path:
        model_url = "/artifacts/umlement.puml"

    return jsonify(
        {
            "success": result.success,
            "error": result.error,
            "progress": progress_lines,
            "diagramUrl": diagram_url,
            "modelUrl": model_url,
            "sampleProjects": SAMPLE_PROJECTS,
            "resolvedPaths": resolved_paths,
        }
    )


@app.get("/artifacts/<path:name>")
def artifacts(name: str):
    artifact_path = MODELS_DIR / name
    return send_file(artifact_path)


if __name__ == "__main__":
    app.run(debug=False)
