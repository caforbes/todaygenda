import datetime as dt
import json
import os
from rich import print
from rich.table import Table
import typer

from src import utils
from src.models import Task

app = typer.Typer()


def load_todaylist() -> dict:
    # load from flat file
    this_dir = os.path.abspath(os.path.dirname(__file__))
    task_file = os.path.join(this_dir, "today.json")
    with open(task_file) as f:
        contents = json.load(f)

    # convert to app objects
    contents["tasks"] = [
        make_task_from_string(task_str) for task_str in contents["tasks"]
    ]
    contents["list_duration"] = utils.deltasum(
        deltas=[task.duration for task in contents["tasks"]]
    )

    return contents


def make_task_from_string(task_string: str) -> Task:
    split_task = utils.parse_out_duration(task_string)
    return make_task(
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
def show_summary() -> None:
    todaylist = load_todaylist()

    if todaylist["tasks"]:
        display_tasks(todaylist["tasks"])
        finish_time_str = utils.duration_to_str(todaylist["list_duration"])
        print(f"Total Time to Finish: {finish_time_str}\n")
    else:
        print("Your todolist is empty!")

    now = dt.datetime.now()
    print(f"Current Time:\t\t{now}")
    endtime = now + todaylist["list_duration"]
    print(f"Expected Finish:\t{endtime}")


if __name__ == "__main__":
    app()
