from datetime import datetime
import json
import os

from fastapi import FastAPI

from db.local import LOCAL_FILE
from src.models import Daylist, Agenda
from src.timeline import build_agenda

app = FastAPI()


def temp_get_daylist() -> Daylist:
    if not os.path.exists(LOCAL_FILE):
        return Daylist()

    with open(LOCAL_FILE) as f:
        content = json.load(f)
    daylist = Daylist.model_validate(content)

    # if daylist is old, build a new one
    if daylist.expiry < datetime.now():
        return Daylist()
    return daylist


@app.get("/")
def read_today() -> Daylist:
    """Read the current list of things to do today.

    Contains a list of pending tasks and done tasks.
    This list expires within a 24-hour window of creation.
    """
    return temp_get_daylist()


@app.get("/agenda")
def read_agenda() -> Agenda:
    """Read a timeline of what to do next.

    Contains a timeline and indicates the overall finish time.
    Includes warnings for if the timeline exceeds the daily list expiry time.
    """
    daylist = temp_get_daylist()
    agenda = build_agenda(daylist)
    return agenda
