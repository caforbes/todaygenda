from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import datetime as dt

from config import Settings

from src.models import Daylist, Agenda
import src.operations as backend


def configure(app: FastAPI, settings: Settings):
    """Set up app settings from env."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
    )


app = FastAPI()
configure(app, backend.SETTINGS)


# Routes


@app.get("/")
def read_root():
    """Basic healthcheck."""
    return "API server is running!"


@app.get("/today")
def read_today(expire: Optional[dt.time] = None) -> Daylist:
    """Read the current list of things to do today.

    Contains a list of pending tasks and done tasks. This list expires within a 24-hour
    window of creation.
    """
    if expire and not expire.tzinfo:
        raise HTTPException(status_code=400, detail="Timezone not provided.")
    return backend.temp_get_or_make_todaylist(expire)


@app.get("/agenda")
def read_agenda(expire: Optional[dt.time] = None) -> Agenda:
    """Read a timeline of what to do next.

    Contains a timeline and indicates the overall finish time. Includes warnings for if
    the timeline exceeds the daily list expiry time.
    """
    if expire and not expire.tzinfo:
        raise HTTPException(status_code=400, detail="Timezone not provided.")
    daylist = backend.temp_get_or_make_todaylist(expire)
    agenda = backend.build_agenda(daylist)
    return agenda
