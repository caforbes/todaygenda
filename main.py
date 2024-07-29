import datetime as dt
import json
import logging
import os
from rich import print
from rich.table import Table
import typer

from src import utils
from src.models import Daylist, Task

app = typer.Typer(no_args_is_help=True)

storage = "daylist.json"
this_dir = os.path.abspath(os.path.dirname(__file__))


def build_from_storage() -> Daylist:
    daylist_file = os.path.join(this_dir, storage)
    if os.path.exists(daylist_file):
        with open(daylist_file) as f:
            daylist = json.load(f)
        daylist = Daylist.model_validate(daylist)
    else:
        daylist = reset_daylist()

    # if daylist is old, build a new one
    if not daylist.is_for_today():
        daylist = reset_daylist()

    return daylist


def send_to_storage(daylist: Daylist) -> None:
    daylist_file = os.path.join(this_dir, storage)
    with open(daylist_file, "w") as writer:
        json.dump(daylist.model_dump(mode="json"), writer, ensure_ascii=False)


def reset_daylist() -> Daylist:
    logging.info("Building new list for today!")
    return Daylist()


def make_task_from_string(task_string: str) -> Task:
    split_task = utils.parse_out_duration(task_string)
    return Task(
        name=split_task["str"],
        duration=utils.duration_from_str(split_task["dur"]),
    )


def make_task(name: str, duration: dt.timedelta) -> Task:
    return Task(name=name, duration=duration)


def display_tasks(task_list: list[Task]) -> None:
    table = Table("#", "Todos", "Time to Finish")
    for idx, task in enumerate(task_list):
        temp_index = idx + 1
        table.add_row(str(temp_index), task.name, task.durationstr())
    print(table)


@app.command()
def add(name: str, minutes: int) -> None:
    daylist = build_from_storage()

    task = make_task(name=name, duration=dt.timedelta(minutes=minutes))
    # TODO: validation for task time length

    daylist.tasks.append(task)
    send_to_storage(daylist)

    print("Added new task to your list!")


@app.command()
def add_task_batch(filename: str) -> None:
    daylist = build_from_storage()

    # load from flat file
    task_file = os.path.join(this_dir, filename)
    with open(task_file) as f:
        contents = json.load(f)

    tasks = [make_task_from_string(task_str) for task_str in contents["tasks"]]
    for task in tasks:
        daylist.tasks.append(task)

    send_to_storage(daylist)
    print(f"Added {len(tasks)} new task(s) to your list!")


@app.command()
def show() -> None:
    daylist = build_from_storage()
    # save in case you built/reset it
    send_to_storage(daylist)

    if daylist.tasks:
        display_tasks(daylist.tasks)
        print(f"Total Time to Finish: {daylist.task_duration()}\n")
    else:
        print("Your todolist is empty!")

    now = dt.datetime.now()
    print(f"Current Time:\t\t{now}")
    endtime = now + daylist.task_duration()
    print(f"Expected Finish:\t{endtime}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app()
