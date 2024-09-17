from typing import Annotated
from fastapi import FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
import datetime as dt

from config import Settings

from src.models import Daylist, Agenda, NewTask, Task
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


# Parameters

user_expiry_type = Query(description="a timezone-aware ISO time string")


# Routes


@app.get("/", summary="Health check")
def read_root():
    """Check if the server is running."""
    return "API server is running!"


@app.get("/today", summary="Read today's todo items")
def read_today(
    response: Response, expire: Annotated[dt.time | None, user_expiry_type] = None
) -> Daylist:
    """Read the current list of things to do today.

    Contains a list of pending tasks and done tasks. This list expires within 24 hours.
    By default, expires at midnight UTC, or you can provide a custom expiration time
    that will be used if a new list needs to be created today.
    """
    user_id = backend.validate_temp_user()
    if expire and not expire.tzinfo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Timezone must be provided.",
        )
    created, daylist = backend.get_or_make_todaylist(user_id, expire)
    if created:
        response.status_code = status.HTTP_201_CREATED
    return daylist


@app.get("/agenda", summary="Read today's agenda")
def read_agenda(
    response: Response, expire: Annotated[dt.time | None, user_expiry_type] = None
) -> Agenda:
    """Read a timeline of what to do next.

    Contains a timeline and indicates the overall finish time. Includes indications if
    the timeline exceeds the expiry time of today's list. You can provide a custom
    expiration time that will be used if a new list needs to be created today.
    """
    user_id = backend.validate_temp_user()
    if expire and not expire.tzinfo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Timezone must be provided.",
        )
    created, daylist = backend.get_or_make_todaylist(user_id, expire)
    if created:
        response.status_code = status.HTTP_201_CREATED
    agenda = backend.build_agenda(daylist)
    return agenda


@app.post(
    "/task", summary="Add a new pending task", status_code=status.HTTP_201_CREATED
)
def create_task(task: NewTask) -> Task:
    """
    FIX: update docs - Read a timeline of what to do next.

    Contains a timeline and indicates the overall finish time. Includes indications if
    the timeline exceeds the expiry time of today's list. You can provide a custom
    expiration time that will be used if a new list needs to be created today.
    """
    user_id = backend.validate_temp_user()
    created_task = backend.create_task(user_id, task)
    if not created_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No list - can't add a new task.",
        )
    return created_task
