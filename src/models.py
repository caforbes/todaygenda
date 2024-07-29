from datetime import datetime, timedelta
from enum import StrEnum, auto
from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated

from src import utils


class TaskStatus(StrEnum):
    PENDING = auto()
    ACTIVE = auto()
    DONE = auto()


class Task(BaseModel):
    name: Annotated[str, StringConstraints(max_length=200)]
    duration: timedelta = Field(default_factory=timedelta)
    status: TaskStatus = TaskStatus.PENDING
    created: datetime = Field(default_factory=datetime.now)

    def durationstr(self) -> str:
        """
        Task duration as a string in format 1m / 2h / 1h20m
        """
        return utils.duration_to_str(self.duration)


class Daylist(BaseModel):
    created: datetime = Field(default_factory=datetime.now)
    tasks: list[Task] = []

    def is_for_today(self) -> bool:
        return self.created.date() == datetime.now().date()

    def task_duration(self) -> timedelta:
        return utils.deltasum(deltas=[task.duration for task in self.tasks])
