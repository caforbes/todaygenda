from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
def read_today() -> Daylist:
    """Read the current list of things to do today.

    Contains a list of pending tasks and done tasks.
    This list expires within a 24-hour window of creation.
    """
    return backend.temp_get_daylist()


@app.get("/agenda")
def read_agenda() -> Agenda:
    """Read a timeline of what to do next.

    Contains a timeline and indicates the overall finish time.
    Includes warnings for if the timeline exceeds the daily list expiry time.
    """
    daylist = backend.temp_get_daylist()
    agenda = backend.build_agenda(daylist)
    return agenda
