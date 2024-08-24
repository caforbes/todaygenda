from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from cli import utils
from src.models import Daylist, Task, TaskStatus


class BaseHasMetadata(BaseModel):
    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(default_factory=datetime.now)

    def mark_updated(self):
        self.updated = datetime.now()


class TaskCLI(BaseHasMetadata, Task):
    def estimatestr(self) -> str:
        """
        Task estimate as a string in format 1m / 2h / 1h20m
        """
        return utils.duration_to_str(self.estimate)

    def mark_done(self):
        """
        Mark task as DONE.
        """
        self.status = TaskStatus.DONE
        self.mark_updated()


class DaylistCLI(BaseHasMetadata, Daylist):
    tasks: list[TaskCLI] = []

    def total_estimate(self) -> timedelta:
        """
        Calculate the length required to complete the current todolist.
        Note: Basic addition is used for now.
        """
        return utils.deltasum(deltas=[task.estimate for task in self.pending_tasks()])

    def is_for_today(self) -> bool:
        """
        Check if the todolist was created on the current day.
        """
        return self.created.date() == datetime.now().date()

    def done_tasks(self) -> list[TaskCLI]:
        """
        Get tasks with status DONE, already complete.
        """
        return [task for task in self.tasks if task.status == TaskStatus.DONE]

    def pending_tasks(self) -> list[TaskCLI]:
        """
        Get tasks with status PENDING, yet to be completed.
        """
        return [task for task in self.tasks if task.status == TaskStatus.PENDING]

    def get_pending_task_at(self, index: int) -> TaskCLI:
        if index < 0:
            raise ValueError("Must provide the exact index.")
        return self.pending_tasks()[index]

    def add_task(self, name=str, estimate=timedelta):
        """
        Add a task to this list.
        """
        task = TaskCLI(name=name, estimate=estimate)
        self.tasks.append(task)
        self.mark_updated()

    def remove_task(self, index: int):
        """
        Remove a task from this list.
        """
        target = self.get_pending_task_at(index)
        self.tasks.remove(target)  # just drop task for now
        self.mark_updated()

    def complete_task(self, index: int):
        """
        Mark a pending task in the list as done.
        """
        target = self.get_pending_task_at(index)
        target.mark_done()  # just drop task for now
        target.mark_updated()
