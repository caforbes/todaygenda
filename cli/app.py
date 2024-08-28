import datetime as dt
import json
import logging
import os
from rich import print
from rich.table import Table
import typer
from typing_extensions import Annotated

from db.local import LOCAL_FILE
from cli.models import DaylistCLI, TaskCLI
from src.utils import PRETTY_DATE_FORMAT, duration_from_str


# Setup

app = typer.Typer(no_args_is_help=True)


# Commands


@app.command()
def show() -> None:
    """Display today's todolist and show your expected completion time."""
    daylist = build_from_storage()
    # save in case you built/reset it
    send_to_storage(daylist)

    if not daylist.pending_tasks:
        if daylist.done_tasks:
            print("You've completed all the tasks in your list!")
        else:
            print("Your todolist is empty!")
        return

    now = dt.datetime.now()
    display_tasks(daylist.pending_tasks, now)
    print(f"Total Time to Finish: {daylist.total_estimate()}\n")
    print(f"{len(daylist.done_tasks)} Tasks Already Completed\n")

    print(f"Current Time:\t\t{now.strftime(PRETTY_DATE_FORMAT)}")
    endtime = now + daylist.total_estimate()
    print(f"Estimated Finish:\t{endtime.strftime(PRETTY_DATE_FORMAT)}")


@app.command()
def add(title: str, estimate: str) -> None:
    """Add a new task to your todolist, including the expected task estimate.

    The estimate can be provided as a string (in format "1h30m"), or as a number of
    minutes (e.g. 90).
    """
    daylist = build_from_storage()
    try:
        minutes = int(estimate)
        delta = dt.timedelta(minutes=minutes)
    except ValueError:
        delta = duration_from_str(dur_str=estimate)

    daylist.add_task(title=title, estimate=delta)
    send_to_storage(daylist)

    print("Added new task to your list!")


@app.command()
def delete(task_number: int) -> None:
    """Permanently remove a task from your todolist."""
    daylist = build_from_storage()
    task_index = task_number - 1

    try:
        daylist.remove_task(task_index)
    except IndexError as e:
        logging.error(f"Couldn't find task #{task_number}!")
        raise e

    send_to_storage(daylist)
    print(f"Removed task #{task_number} from your list!")


@app.command()
def complete(task_number: Annotated[int, typer.Argument()] = 1) -> None:
    """Mark a task in the todolist as done/completed.

    Defaults to completing the first task.
    """
    daylist = build_from_storage()
    task_index = task_number - 1

    try:
        daylist.complete_task(task_index)
    except IndexError as e:
        logging.error(f"Couldn't find task #{task_number}!")
        raise e

    send_to_storage(daylist)
    print("Another task completed!")


# Helpers


def build_from_storage() -> DaylistCLI:
    """Check storage for the current daylist.

    If it exists, return it, otherwise create a new one.
    """
    if not os.path.exists(LOCAL_FILE):
        daylist = reset_daylist()
    else:
        with open(LOCAL_FILE) as f:
            daylist = json.load(f)
        daylist = DaylistCLI.model_validate(daylist)

        # if daylist is old, build a new one
        if daylist.is_expired():
            daylist = reset_daylist()

    return daylist


def send_to_storage(daylist: DaylistCLI) -> None:
    """Save the current daylist to storage."""
    with open(LOCAL_FILE, "w") as writer:
        json.dump(daylist.model_dump(mode="json"), writer, ensure_ascii=False)


def reset_daylist() -> DaylistCLI:
    """Build a fresh daylist, with prompt as needed."""
    print("Building new list for today!")
    return DaylistCLI()


def display_tasks(task_list: list[TaskCLI], start_time: dt.datetime) -> None:
    """Print a pretty table of the current set of tasks."""
    table = Table("#", "Todos", "Time estimate", "Expected start")
    for idx, task in enumerate(task_list):
        temp_index = idx + 1
        table.add_row(
            str(temp_index),
            task.title,
            task.estimatestr(),
            start_time.strftime(PRETTY_DATE_FORMAT),
        )
        start_time += task.estimate

    print(table)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()
