import datetime as dt
import json
import os
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


@app.command()
def show_summary() -> None:
    todaylist = load_todaylist()

    if todaylist["tasks"]:
        print("Tasks:")
        for task in todaylist["tasks"]:
            print(
                "\t", task["name"], "\t\t", utils.duration_secs_to_str(task["duration"])
            )
        finish_time_str = utils.duration_secs_to_str(
            int(todaylist["total_duration"].total_seconds())
        )
        print(f"Time to finish: {finish_time_str}\n")
    # if todaylist["events"]:
    #     print("Events:")
    #     for event in todaylist["events"]:
    #         print("\t", event)

    now = dt.datetime.now()
    print(f"Current time:\t\t{now}")
    print(f"You could finish by:\t{now + todaylist["total_duration"]}")


if __name__ == "__main__":
    app()
