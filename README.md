# TimeTruth – AI Task Duration Predictor (Project 84)

A full-stack machine learning web app. It predicts how long a task will take, tracks the real time, and learns from completed tasks.

```
timetruth-fullstack/
  ml/          Roshan B        ML pipeline: features, training, prediction, explanations
  backend/     Rithwik Suthari FastAPI REST API, serves the frontend
  data/        Mokireddy Lohith Reddy  Data layer: schemas, dataset, SQLite storage
  frontend/    A Shashank      index.html, styles.css, app.js
  requirements.txt             shared
```

| Member | Roll No. | Files they own |
|---|---|---|
| Roshan B | 24WU0102163 | `ml/features.py`, `ml/train.py`, `ml/predict.py` |
| Rithwik Suthari | 24WU0102167 | `backend/main.py` |
| Mokireddy Lohith Reddy | 24WU0102232 | `data/schema.py`, `data/dataset.py`, `data/database.py` |
| A Shashank | 24WU0102162 | `frontend/index.html`, `frontend/styles.css`, `frontend/app.js` |

## Setup and run

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m ml.train                   # trains the model and saves ml/model.joblib
uvicorn backend.main:app --reload    # starts the API and the frontend
```

Open http://127.0.0.1:8000. The API docs are at http://127.0.0.1:8000/docs.

## API

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/predict` | Predict a task's duration (with explanation and personal adjustment) |
| POST | `/api/tasks` | Save a completed task |
| GET | `/api/tasks` | List completed tasks |
| DELETE | `/api/tasks/{id}` | Delete one task |
| DELETE | `/api/tasks` | Clear all history |
| GET | `/api/stats` | Accuracy numbers and model comparison |
| POST | `/api/demo` | Add eight demo tasks |

## Interfaces between parts
These names are the contract between the team's files. Do not rename them without telling the team.
- `data/schema.py`: `TaskInput`, `TaskRecord`
- `data/database.py`: `insert_task`, `list_tasks`, `delete_task`, `clear_tasks`
- `data/dataset.py`: `generate_history`, `DEMO_NAMES`
- `ml/predict.py`: `predict_base`, `explain`, `load_bundle`
- `backend/main.py`: the `/api` routes above

## Git workflow (every member)

```bash
git clone https://github.com/OWNER/timetruth.git
cd timetruth
git checkout -b part/<your-name>
git add <your-files>                 # only the files you own
git commit -m "<what you built>"
git push -u origin part/<your-name>
```

Then open a Pull Request into `main`. Run `git pull origin main` before pushing again.
If you need a change in someone else's file, open an Issue and tag them.

## Notes
- The training data is generated, not real. Replace `data/dataset.py` with real completion logs when the team has them.
- `ml/model.joblib` and `data/timetruth.db` are created at runtime and are ignored by Git.
