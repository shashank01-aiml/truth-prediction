"""Owner: Mokireddy Lohith Reddy — generates the historical task dataset used for training and demos.
The data is synthetic: real completion logs should replace it when available."""
import numpy as np

CATEGORIES = ["Programming", "Writing", "Studying", "Design"]
PRIORITIES = ["Low", "Medium", "High"]
DEMO_NAMES = ["Python assignment", "ML project", "Research paper", "PPT preparation",
              "Coding practice", "Essay draft", "Exam revision", "Database design"]
BASE_HOURS = {"Programming": 2.5, "Writing": 1.8, "Studying": 3.0, "Design": 2.2}
DIFFICULTY_MULT = {"Easy": 0.6, "Medium": 1.0, "Hard": 1.8}
EXPERIENCE_MULT = {"Beginner": 1.6, "Intermediate": 1.2, "Expert": 0.9}


def generate_history(n: int = 400, seed: int | None = 84) -> list[dict]:
    rng = np.random.default_rng(seed)
    tasks = []
    for _ in range(n):
        cat = CATEGORIES[rng.integers(len(CATEGORIES))]
        diff = list(DIFFICULTY_MULT)[rng.integers(3)]
        exp = list(EXPERIENCE_MULT)[rng.integers(3)]
        pri = PRIORITIES[rng.integers(3)]
        actual = max(0.25, BASE_HOURS[cat] * DIFFICULTY_MULT[diff] * EXPERIENCE_MULT[exp] * (0.75 + 0.5 * rng.random()))
        estimate = actual * (0.5 + 0.6 * rng.random())  # people tend to underestimate
        tasks.append({"category": cat, "difficulty": diff, "experience": exp, "priority": pri,
                      "estimate": round(estimate, 2), "actual": round(actual, 2)})
    return tasks
