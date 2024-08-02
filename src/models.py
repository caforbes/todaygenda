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
    name: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    estimate: timedelta
    status: TaskStatus = TaskStatus.PENDING

    @field_validator("estimate")
    @classmethod
    def estimate_under_24h(cls, dur: timedelta) -> timedelta:
        """
        Ensure time estimates can't exceed 1 day / 24h.
        """
        if dur.days > 0:
            raise ValueError("Task time estimates must be less than 24 hours")
        return dur

    @field_validator("estimate")
    @classmethod
    def estimate_minimum(cls, dur: timedelta) -> timedelta:
        """
        Ensure task estimates are above zero.
        Note: Tasks with no estimate provided receive 0 by default - require correction.
        """
        if dur.total_seconds() <= 0:
            raise ValueError("Task must have a provided time estimate.")
        return dur

    def estimatestr(self) -> str:
        """
        Task estimate as a string in format 1m / 2h / 1h20m
        """
        return utils.duration_to_str(self.estimate)


class Daylist(BaseModelWithMetadata):
    tasks: list[Task] = []

    def total_estimate(self) -> timedelta:
        """
        Calculate the length required to complete the current todolist.
        Note: Basic addition is used for now.
        """
        return utils.deltasum(deltas=[task.estimate for task in self.tasks])

    def is_for_today(self) -> bool:
        """
        Check if the todolist was created on the current day.
        """
        return self.created.date() == datetime.now().date()

    def add_task(self, task: Task):
        """
        Add a task to this list.
        """
        if task in self.tasks:
            return

        self.tasks.append(task)
        self.mark_updated()
