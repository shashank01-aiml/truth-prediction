"""Owner: Roshan B — loads the trained model, predicts, and explains each prediction
using real model contributions (coefficient × (feature value − training average))."""
from functools import lru_cache
import joblib
import numpy as np
from ml.features import to_row
from ml.train import MODEL_PATH, train

# How each feature is described to the user
TEXT = [
    lambda t: f"Difficulty: {t['difficulty']}",
    lambda t: f"Experience: {t['experience']}",
    lambda t: f"Priority: {t['priority']}",
    lambda t: f"Category: {t['category']}",
    lambda t: f"Category: {t['category']}",
    lambda t: f"Category: {t['category']}",
    lambda t: f"Estimate of {t['estimate']} h",
]


@lru_cache(maxsize=1)
def load_bundle() -> dict:
    return joblib.load(MODEL_PATH) if MODEL_PATH.exists() else train()


def predict_base(task: dict) -> float:
    model = load_bundle()["model"]
    return max(0.25, float(model.predict([to_row(task)])[0]))


def explain(task: dict, top: int = 3) -> list[dict]:
    b = load_bundle()
    row = np.array(to_row(task))
    contrib = b["model"].coef_ * (row - np.array(b["feature_means"]))
    items = []
    for i, c in enumerate(contrib):
        if 3 <= i <= 5 and row[i] == 0:  # skip category columns that do not apply
            continue
        items.append({"text": TEXT[i](task), "hours": round(float(c), 2)})
    return sorted(items, key=lambda d: -abs(d["hours"]))[:top]
