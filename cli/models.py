from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field, model_validator

from src import utils
from src.models import BaseDaylist, Task, TaskStatus


class BaseHasMetadata(BaseModel):
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

    def mark_updated(self):
        self.updated = datetime.now()


class TaskCLI(BaseHasMetadata, Task):
    id: int = 0

    def estimatestr(self) -> str:
        """Task estimate as a string in format 1m / 2h / 1h20m."""
        return utils.duration_to_str(self.estimate)

    def mark_done(self):
        """Mark task as DONE."""
        self.status = TaskStatus.DONE
        self.mark_updated()


class DaylistCLI(BaseHasMetadata, BaseDaylist):
    pending_tasks: list[TaskCLI] = []
    done_tasks: list[TaskCLI] = []

    @model_validator(mode="after")
    def check_tasks_by_status(self):
        if any(task.status != TaskStatus.PENDING for task in self.pending_tasks):
            raise ValueError("Non-pending task found in list")
        if any(task.status != TaskStatus.DONE for task in self.done_tasks):
            raise ValueError("Non-done task found in list")

        self.pending_tasks = [
            TaskCLI(title=task.title, estimate=task.estimate)
            for task in self.pending_tasks
        ]
        self.done_tasks = [
            TaskCLI(title=task.title, estimate=task.estimate)
            for task in self.done_tasks
        ]
        return self

    def total_estimate(self) -> timedelta:
        """Calculate the length required to complete the current todolist.

        Note: Basic addition is used for now.
        """
        return utils.deltasum(deltas=[task.estimate for task in self.pending_tasks])

    def is_expired(self) -> bool:
        """Check if the todolist is expired."""
        return self.expiry < datetime.now(timezone.utc)

    def get_pending_task_at(self, index: int) -> TaskCLI:
        if index not in range(0, len(self.pending_tasks)):
            raise IndexError("Must provide the exact index.")
        return self.pending_tasks[index]

    def add_task(self, title=str, estimate=timedelta):
        """Add a task to this list."""
        task = TaskCLI(title=title, estimate=estimate)
        self.pending_tasks.append(task)
        self.mark_updated()

    def remove_task(self, index: int):
        """Remove a task from this list."""
        target = self.get_pending_task_at(index)
        self.pending_tasks.remove(target)
        self.mark_updated()

    def complete_task(self, index: int):
        """Mark a pending task in the list as done."""
        target = self.get_pending_task_at(index)
        target.mark_done()  # just drop task for now
        self.pending_tasks.remove(target)
        self.done_tasks.append(target)
        target.mark_updated()
