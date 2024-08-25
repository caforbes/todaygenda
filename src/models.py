from datetime import datetime, timedelta
from enum import StrEnum, auto
from pydantic import BaseModel, Field, StringConstraints, field_validator
from typing_extensions import Annotated

import src.utils as utils


class TaskStatus(StrEnum):
    PENDING = auto()
    DONE = auto()


class Task(BaseModel):
    name: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    estimate: timedelta = timedelta(minutes=20)
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
        """
        if dur.total_seconds() <= 0:
            raise ValueError("Task must have a provided time estimate.")
        return dur


class Daylist(BaseModel):
    # TODO: expiry: datetime = Field(default_factory=utils.next_midnight)
    pending_tasks: list[Task] = []
    done_tasks: list[Task] = []
