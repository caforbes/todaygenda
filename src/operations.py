import datetime as dt
from typing import Optional

from config import get_settings
from db.connect import query_connect
from src.models import Daylist, Agenda, AgendaItem
from src.utils import next_midnight, next_timepoint


SETTINGS = get_settings()
DB = query_connect(SETTINGS.database_url)


def temp_get_or_make_todaylist(user_expiry: Optional[dt.time] = None) -> Daylist:
    """Get or create an unexpired daylist for today, for a placeholder user."""
    # get this user - MVP just get the top user
    temp_user = DB.get_anon_user()
    if temp_user is None:
        # BOOKMARK: add handling in api - 400 etc
        raise ValueError("Attempt to retrieve user that does not exist.")

    uid = temp_user["id"]
    with DB.transaction():
        # BOOKMARK: eventually, we should supply a userid from the current session
        active_daylist = DB.get_active_daylist(user_id=uid)

        if active_daylist:
            active_daylist["pending_tasks"] = list(DB.get_pending_tasks(user_id=uid))
        else:
            # handle optional user-provided expiry time
            if user_expiry:
                set_expiry = next_timepoint(user_expiry)
            else:
                set_expiry = next_midnight("system")
            DB.add_daylist(user_id=uid, expiry=set_expiry)
            active_daylist = DB.get_active_daylist(user_id=uid)

    return Daylist.model_validate(active_daylist)


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
