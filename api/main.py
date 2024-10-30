from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
import datetime as dt

from config import Settings

from api.utils import error_detail
from api.routes import auth, task
from api.routes.auth import get_current_user
from src.models import Daylist, Agenda, User
import src.operations as backend


def configure(app: FastAPI, settings: Settings):
    """Set up app settings from env."""
    cors_settings = {
        "allow_origins": settings.allowed_origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "HEAD", "OPTIONS"],
        "allow_headers": [
            "Access-Control-Allow-Headers",
            "Content-Type",
            "Authorization",
            "Access-Control-Allow-Origin",
        ],
    }
    if settings.allowed_origins_regex:
        cors_settings["allow_origin_regex"] = settings.allowed_origins_regex

    app.add_middleware(CORSMiddleware, **cors_settings)


app = FastAPI()
app.include_router(auth.router)
app.include_router(task.router)

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
    current_user: Annotated[User, Depends(get_current_user)],
    response: Response,
    expire: Annotated[dt.time | None, user_expiry_type] = None,
) -> Daylist:
    """Read the current list of things to do today.

    Contains a list of pending tasks and done tasks. This list expires within 24 hours.
    By default, expires at midnight UTC, or you can provide a custom expiration time
    that will be used if a new list needs to be created today.
    """
    if expire and not expire.tzinfo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_detail(
                "Expire time parameter must have a timezone.", errtype="time_parsing"
            ),
        )
    created, daylist = backend.get_or_make_todaylist(current_user.id, expire)
    if created:
        response.status_code = status.HTTP_201_CREATED
    return daylist


@app.get("/agenda", summary="Read today's agenda")
def read_agenda(
    current_user: Annotated[User, Depends(get_current_user)],
    response: Response,
    expire: Annotated[dt.time | None, user_expiry_type] = None,
) -> Agenda:
    """Read a timeline of what to do next.

    Contains a timeline and indicates the overall finish time. Includes indications if
    the timeline exceeds the expiry time of today's list. You can provide a custom
    expiration time that will be used if a new list needs to be created today.
    """
    if expire and not expire.tzinfo:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_detail(
                "Expire time parameter must have a timezone.", errtype="time_parsing"
            ),
        )
    created, daylist = backend.get_or_make_todaylist(current_user.id, expire)
    if created:
        response.status_code = status.HTTP_201_CREATED
    agenda = backend.build_agenda(daylist)
    return agenda
