from datetime import datetime, timedelta, timezone
from pydantic import AwareDatetime, BaseModel, Field, StringConstraints, field_validator
from typing_extensions import Annotated

import src.utils as utils


class NewTask(BaseModel):
    title: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    estimate: timedelta

    @field_validator("estimate")
    @classmethod
    def estimate_under_24h(cls, dur: timedelta) -> timedelta:
        """Ensure time estimates can't exceed 1 day / 24h."""
        if dur.days > 0:
            raise ValueError("Task time estimates must be less than 24 hours")
        return dur

    @field_validator("estimate")
    @classmethod
    def estimate_minimum(cls, dur: timedelta) -> timedelta:
        """Ensure task estimates are above zero."""
        if dur.total_seconds() <= 0:
            raise ValueError("Task must have a provided time estimate.")
        return dur


class Task(NewTask):
    id: int
    done: bool = False


class BaseDaylist(BaseModel):
    expiry: AwareDatetime = Field(default_factory=utils.next_midnight)

    @field_validator("expiry")
    @classmethod
    def expiry_limits(cls, expiry: datetime) -> datetime:
        """Ensure expiry is less than 24h from now."""
        day_from_now = datetime.now(timezone.utc) + timedelta(days=1)
        if expiry >= day_from_now:
            raise ValueError("Today's list expires after maximum 24 hours")
        return expiry


class Daylist(BaseDaylist):
    id: int
    pending_tasks: list[Task] = []
    done_tasks: list[Task] = []


class AgendaItem(BaseModel):
    title: str
    start: AwareDatetime
    end: AwareDatetime


class Agenda(BaseModel):
    timeline: list[AgendaItem]
    finish: AwareDatetime
    expiry: AwareDatetime
    past_expiry: bool


class ActionResult(BaseModel):
    success: list[int] = []


# Auth


class User(BaseModel):
    id: int
    email: str | None = None
    registered_at: datetime | None = None


class UserFromDB(User):
    password_hash: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_sub: str
