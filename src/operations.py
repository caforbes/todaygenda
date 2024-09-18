import datetime as dt
from typing import Optional

from sqlalchemy.exc import IntegrityError

from config import get_settings
from db.connect import query_connect
from src.models import Daylist, Agenda, AgendaItem, Task, NewTask
from src.utils import next_midnight, next_timepoint


SETTINGS = get_settings()
DB = query_connect(SETTINGS.database_url)


def validate_temp_user() -> int:
    # MVP return the top anonymous user
    temp_user = DB.get_anon_user()
    if temp_user is None:
        raise ValueError("User not found")  # BOOKMARK: better validation later
    return temp_user["id"]


def get_or_make_todaylist(
    uid: int, user_expiry: Optional[dt.time] = None
) -> tuple[bool, Daylist]:
    """Get or create an unexpired daylist for today, for a placeholder user.

    Returns a tuple:
    - bool: does this function call create the list or merely get it?
    - list: the list content
    """
    is_new = False
    with DB.transaction():
        active_daylist = DB.get_active_daylist(user_id=uid)

        if active_daylist:
            active_daylist["pending_tasks"] = list(DB.get_pending_tasks(user_id=uid))
        else:
            # handle optional user-provided expiry time
            if user_expiry:
                set_expiry = next_timepoint(user_expiry)
            else:
                set_expiry = next_midnight("utc")
            DB.add_daylist(user_id=uid, expiry=set_expiry)
            active_daylist = DB.get_active_daylist(user_id=uid)
            is_new = True

    return (is_new, Daylist.model_validate(active_daylist))


def build_agenda(daylist: Daylist) -> Agenda:
    timestamp = dt.datetime.now(dt.timezone.utc).replace(second=0, microsecond=0)
    items = []
    for task in daylist.pending_tasks:
        items.append(
            AgendaItem(
                title=task.title,
                start=timestamp,
                end=timestamp + task.estimate,
            )
        )
        timestamp += task.estimate

    return Agenda(
        timeline=items,
        expiry=daylist.expiry,
        finish=timestamp,
        past_expiry=(timestamp > daylist.expiry),
    )


def create_task(uid: int, task: NewTask) -> Task | None:
    """Create a new task in the user's list and return it."""
    try:
        with DB.transaction():
            task_id = DB.add_task_for_user(
                user_id=uid, title=task.title, estimate=task.estimate
            )
            new_task = DB.get_task(id=task_id)
            return Task(**new_task)  # type: ignore
    except IntegrityError:
        return None
