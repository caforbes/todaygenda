from datetime import datetime
import json
import os

from fastapi import FastAPI

from db.local import LOCAL_FILE
from src.models import Daylist, TodayView

app = FastAPI()


@app.get("/")
def read_today() -> TodayView:
    """Read the current list and projected finish time for today."""

    if not os.path.exists(LOCAL_FILE):
        return Daylist()

    with open(LOCAL_FILE) as f:
        daylist = json.load(f)
    daylist = Daylist.model_validate(daylist)

    # if daylist is old, build a new one
    if not daylist.is_for_today():
        daylist = Daylist()

    return TodayView(today=daylist, time_to_finish=daylist.total_estimate())
