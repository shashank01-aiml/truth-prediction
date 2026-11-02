"""Owner: Roshan B — ML pipeline: feature engineering.
Turns one task (a dict) into the numeric row the model reads."""
import numpy as np

DIFFICULTY = {"Easy": 1, "Medium": 2, "Hard": 3}
EXPERIENCE = {"Beginner": 1, "Intermediate": 2, "Expert": 3}
PRIORITY = {"Low": 1, "Medium": 2, "High": 3}
# "Design" is the baseline category: it is all zeros in the three category columns.
FEATURE_NAMES = ["Difficulty", "Experience", "Priority", "Writing", "Studying", "Programming", "Estimate"]


def to_row(task: dict) -> list[float]:
    c = task["category"]
    return [DIFFICULTY[task["difficulty"]], EXPERIENCE[task["experience"]], PRIORITY[task["priority"]],
            float(c == "Writing"), float(c == "Studying"), float(c == "Programming"), float(task["estimate"])]


def to_matrix(tasks: list[dict]) -> np.ndarray:
    return np.array([to_row(t) for t in tasks], dtype=float)
