from datetime import datetime, timedelta
from enum import StrEnum, auto
from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated

from src.utils import duration_to_str


class TaskStatus(StrEnum):
    PENDING = auto()
    ACTIVE = auto()
    DONE = auto()


class Task(BaseModel):
    name: Annotated[str, StringConstraints(max_length=200)]
    duration: timedelta = Field(default_factory=timedelta)
    status: TaskStatus = TaskStatus.PENDING
    created: timedelta = Field(default_factory=datetime.now)

    def durationstr(self) -> str:
        """
        Task duration as a string in format 1m / 2h / 1h20m
        """
        return duration_to_str(self.duration)
