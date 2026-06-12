import os
import uuid
import json
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


from src.analyzer import analyze_prompt
from src.improver import run_improvement_cycle
from src.stress_tester import run_stress_test
from src.exporter import export_artifacts


# Minimal local API to wrap existing CLI pipeline.
# Frontend is served as static files (see web/ directory).

APP_DIR = Path(__file__).parent
EXPORTS_DIR = APP_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Prompt Inspector UI API")

WEB_DIR = Path(__file__).parent / "web"


@app.middleware("http")
async def no_cache_middleware(request, call_next):
    response = await call_next(request)
    if request.url.path.endswith((".css", ".js", ".html")) or request.url.path == "/":
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


# Allow local dev usage.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InspectRequest(BaseModel):
    prompt: str


class InspectResponse(BaseModel):
    request_id: str
    export_path: str
    analysis: Dict[str, Any]
    comparison: Dict[str, Any]
    stress_results: list


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/inspect", response_model=InspectResponse)
def inspect(req: InspectRequest):
    prompt = (req.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    analysis = analyze_prompt(prompt)
    if not analysis:
        raise HTTPException(status_code=500, detail="analysis failed")

    comparison = run_improvement_cycle(prompt, analysis)

    stress_results = run_stress_test(analysis.improved_prompt, analysis.adversarial_variants)

    export_path = export_artifacts(prompt, analysis, comparison, stress_results)

    request_id = str(uuid.uuid4())

    return InspectResponse(
        request_id=request_id,
        export_path=str(export_path),
        analysis=analysis.model_dump(),
        comparison=comparison.model_dump(),
        stress_results=[s.model_dump() for s in (stress_results or [])],
    )


app.mount(
    "/",
    StaticFiles(directory=str(WEB_DIR), html=True),
    name="web",
)

