import datetime as dt
import json
import os
from rich import print
from rich.table import Table
import typer

from src import utils

app = typer.Typer()


def load_todaylist() -> dict:
    # load from flat file
    this_dir = os.path.abspath(os.path.dirname(__file__))
    task_file = os.path.join(this_dir, "today.json")
    with open(task_file) as f:
        contents = json.load(f)

    # convert to app objects
    contents["tasks"] = [make_new_task(task_str) for task_str in contents["tasks"]]
    contents["total_duration"] = utils.total_delta(
        all_durations=[task["duration"] for task in contents["tasks"]]
    )

    return contents


def make_new_task(task_string: str) -> dict:
    split_task = utils.parse_out_duration(task_string)

    task = {
        "name": split_task["str"],
        "duration": utils.duration_str_to_secs(split_task["dur"]),
        "status": "new",
    }
    return task


def display_tasks(task_list: list[dict]) -> None:
    table = Table("Todos", "Time to Finish")
    for task in task_list:
        table.add_row(task["name"], utils.duration_secs_to_str(task["duration"]))
    print(table)


@app.command()
def show_summary() -> None:
    todaylist = load_todaylist()

    if todaylist["tasks"]:
        display_tasks(todaylist["tasks"])
        finish_time_str = utils.duration_secs_to_str(
            int(todaylist["total_duration"].total_seconds())
        )
        print(f"Total Time to Finish: {finish_time_str}\n")

    now = dt.datetime.now()
    print(f"Current Time:\t\t{now}")
    print(f"Expected Finish:\t{now + todaylist["total_duration"]}")


if __name__ == "__main__":
    app()
