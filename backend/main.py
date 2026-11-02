"""Owner: Rithwik Suthari — FastAPI backend: REST API plus serving of the frontend.
Run from the project root:  uvicorn backend.main:app --reload   then open http://127.0.0.1:8000"""
from pathlib import Path
import numpy as np
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from data import database as db
from data.dataset import DEMO_NAMES, generate_history
from data.schema import TaskInput, TaskRecord
from ml.predict import explain, load_bundle, predict_base

app = FastAPI(title="TimeTruth API")
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


def personal_factor(history: list[dict]) -> tuple[float, float]:
    """Scale predictions by how much longer this user usually takes.
    Capped at ±50%; full weight after 10 completed tasks."""
    if not history:
        return 1.0, 1.0
    ratio = float(np.mean([t["actual_hours"] / t["base_hours"] for t in history]))
    conf = min(len(history) / 10, 1.0)
    return 1 + max(-0.5, min(0.5, ratio - 1)) * conf, ratio


@app.post("/api/predict")
def predict(t: TaskInput):
    task = t.model_dump()
    history = db.list_tasks()
    base = predict_base(task)
    factor, ratio = personal_factor(history)
    return {"task": task, "base_hours": round(base, 2), "factor": round(factor, 3), "ratio": round(ratio, 3),
            "predicted_hours": round(max(0.25, base * factor), 2), "explanation": explain(task),
            "history_count": len(history)}


@app.post("/api/tasks")
def add_task(r: TaskRecord):
    rec = r.model_dump()
    rec["id"] = db.insert_task(rec)
    return rec


@app.get("/api/tasks")
def list_tasks():
    return db.list_tasks()


@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    db.delete_task(task_id)
    return {"ok": True}


@app.delete("/api/tasks")
def clear_tasks():
    db.clear_tasks()
    return {"ok": True}


@app.get("/api/stats")
def stats():
    h = db.list_tasks()
    factor, _ = personal_factor(h)
    errors = [abs(t["actual_hours"] - t["predicted_hours"]) for t in h]
    within = sum(e / t["actual_hours"] <= 0.2 for e, t in zip(errors, h)) / len(h) * 100 if h else 0
    return {"count": len(h), "avg_error_hours": float(np.mean(errors)) if h else None,
            "within_20_percent": round(within, 1), "factor": round(factor, 3),
            "model_report": load_bundle()["report"]}


@app.post("/api/demo")
def demo():
    """Adds eight sample tasks that take about 30% longer than the base prediction."""
    rng = np.random.default_rng()
    for name, t in zip(DEMO_NAMES, generate_history(8, seed=None)):
        base = predict_base(t)
        db.insert_task({**t, "name": name, "base_hours": round(base, 2), "predicted_hours": round(base, 2),
                        "actual_hours": round(base * 1.3 * (0.9 + 0.2 * rng.random()), 2)})
    return {"added": 8}


# Frontend is served last so /api routes take priority
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
