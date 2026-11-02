"""Owner: Roshan B — trains the linear regression model, evaluates it, saves it.
Run from the project root:  python -m ml.train"""
from pathlib import Path
import joblib
import numpy as np
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from data.dataset import generate_history
from ml.features import FEATURE_NAMES, to_matrix

MODEL_PATH = Path(__file__).with_name("model.joblib")


def evaluate(name, y_true, y_pred) -> dict:
    return {"model": name, "MAE": float(mean_absolute_error(y_true, y_pred)),
            "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))), "R2": float(r2_score(y_true, y_pred))}


def train(n: int = 400, seed: int = 84) -> dict:
    tasks = generate_history(n, seed)
    X = to_matrix(tasks)
    y = np.array([t["actual"] for t in tasks])
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed)
    model = LinearRegression().fit(X_tr, y_tr)
    baseline = DummyRegressor(strategy="mean").fit(X_tr, y_tr)
    bundle = {
        "model": model,
        "feature_means": X_tr.mean(axis=0).tolist(),
        "feature_names": FEATURE_NAMES,
        "report": [evaluate("Baseline (average)", y_te, baseline.predict(X_te)),
                   evaluate("Linear regression", y_te, model.predict(X_te))],
    }
    joblib.dump(bundle, MODEL_PATH)
    return bundle


if __name__ == "__main__":
    b = train()
    for r in b["report"]:
        print(f"{r['model']:<22} MAE={r['MAE']:.3f}  RMSE={r['RMSE']:.3f}  R2={r['R2']:.3f}")
    print("Saved", MODEL_PATH)
