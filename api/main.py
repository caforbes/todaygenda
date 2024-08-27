from datetime import datetime
import json
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import Settings, get_settings
from db.local import LOCAL_FILE
from src.models import Daylist, Agenda
from src.operations import build_agenda


def configure(app: FastAPI, settings: Settings):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
    )


app = FastAPI()
configure(app, get_settings())


# DB


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


# Routes


@app.get("/")
def read_root():
    """Basic healthcheck."""
    return "API server is running!"


@app.get("/today")
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
