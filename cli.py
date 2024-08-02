import datetime as dt
from dotenv import load_dotenv
import json
import logging
import os
from rich import print
from rich.table import Table
import typer

from src import utils
from src.models import Daylist, Task

app = typer.Typer(no_args_is_help=True)

load_dotenv()
storage = os.getenv("DAYLIST_FILE")
this_dir = os.path.abspath(os.path.dirname(__file__))
daylist_file = os.path.join(this_dir, storage)


def build_from_storage() -> Daylist:
    """
    Check storage for the current daylist.
    If it exists, return it, otherwise create a new one.
    """
    if not os.path.exists(daylist_file):
        daylist = reset_daylist()
    else:
        with open(daylist_file) as f:
            daylist = json.load(f)
        daylist = Daylist.model_validate(daylist)

        # if daylist is old, build a new one
        if not daylist.is_for_today():
            daylist = reset_daylist()

    return daylist


def send_to_storage(daylist: Daylist) -> None:
    """
    Save the current daylist to storage.
    """
    with open(daylist_file, "w") as writer:
        json.dump(daylist.model_dump(mode="json"), writer, ensure_ascii=False)


def reset_daylist() -> Daylist:
    """
    Build a fresh daylist, with prompt as needed.
    """
    logging.info("Building new list for today!")
    return Daylist()


# TODO: fix parsing duration on CLI (no tab character)
# def make_task_from_string(task_string: str) -> Task:
#     """
#     Parse a string to find the right details, build a new Task from it.
#     """
#     split_task = utils.parse_out_duration(task_string)
#     return Task(
#         name=split_task["str"],
#         duration=utils.duration_from_str(split_task["dur"]),
#     )


def make_task(name: str, duration: dt.timedelta) -> Task:
    """
    Build a new Task from provided details.
    """
    return Task(name=name, duration=duration)


def display_tasks(task_list: list[Task]) -> None:
    """
    Print a pretty table of the current set of tasks.
    """
    table = Table("#", "Todos", "Time to Finish")
    for idx, task in enumerate(task_list):
        temp_index = idx + 1
        table.add_row(str(temp_index), task.name, task.durationstr())
    print(table)


@app.command()
def add(name: str, minutes: int) -> None:
    """
    Add a new task to your todolist, proving the expected task duration in minutes.
    """
    daylist = build_from_storage()

    task = make_task(name=name, duration=dt.timedelta(minutes=minutes))

    daylist.add_task(task)
    send_to_storage(daylist)

    print("Added new task to your list!")


# @app.command()
# def add_string(task_text: str) -> None:
#     daylist = build_from_storage()

#     task = make_task_from_string(task_text)
#     daylist.add_task(task)

#     send_to_storage(daylist)
#     print(f"Added new task to your list!")


@app.command()
def show() -> None:
    """
    Print today's todolist and your expected completion time.
    """
    daylist = build_from_storage()
    # save in case you built/reset it
    send_to_storage(daylist)

    if not daylist.tasks:
        print("Your todolist is empty!")
        return

    display_tasks(daylist.tasks)
    print(f"Total Time to Finish: {daylist.task_duration()}\n")

    now = dt.datetime.now()
    print(f"Current Time:\t\t{now}")
    endtime = now + daylist.task_duration()
    print(f"Expected Finish:\t{endtime}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()
