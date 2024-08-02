from datetime import datetime, timedelta
from enum import StrEnum, auto
from pydantic import BaseModel, Field, StringConstraints, field_validator
from typing_extensions import Annotated

from src import utils


class BaseModelWithMetadata(BaseModel):
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

    def mark_updated(self):
        self.updated = datetime.now()


class TaskStatus(StrEnum):
    PENDING = auto()
    ACTIVE = auto()
    DONE = auto()


class Task(BaseModelWithMetadata):
    name: Annotated[str, StringConstraints(max_length=200)]
    duration: timedelta = Field(default_factory=timedelta)
    status: TaskStatus = TaskStatus.PENDING

    @field_validator("duration")
    @classmethod
    def duration_less_than_24h(cls, dur: timedelta) -> timedelta:
        if dur.days > 0:
            raise ValueError("Task cannot be longer than 24 hours")
        return dur

    def durationstr(self) -> str:
        """
        Task duration as a string in format 1m / 2h / 1h20m
        """
        return utils.duration_to_str(self.duration)


class Daylist(BaseModelWithMetadata):
    tasks: list[Task] = []

    def task_duration(self) -> timedelta:
        return utils.deltasum(deltas=[task.duration for task in self.tasks])

    def is_for_today(self) -> bool:
        return self.created.date() == datetime.now().date()

    def add_task(self, task: Task):
        if task in self.tasks:
            raise ValueError("This task is already on your list")

        self.tasks.append(task)
        self.mark_updated()
