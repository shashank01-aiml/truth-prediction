"""Owner: Mokireddy Lohith Reddy — data schemas. Every task entering the system is validated here."""
from typing import Literal
from pydantic import BaseModel, Field, field_validator

Category = Literal["Programming", "Writing", "Studying", "Design"]
Difficulty = Literal["Easy", "Medium", "Hard"]
Experience = Literal["Beginner", "Intermediate", "Expert"]
Priority = Literal["Low", "Medium", "High"]


class TaskInput(BaseModel):
    name: str = Field(default="Untitled task", max_length=80)
    category: Category
    difficulty: Difficulty
    experience: Experience
    priority: Priority
    estimate: float = Field(gt=0, le=200)

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        return v.strip() or "Untitled task"


class TaskRecord(TaskInput):
    base_hours: float = Field(gt=0)
    predicted_hours: float = Field(gt=0)
    actual_hours: float = Field(gt=0)
