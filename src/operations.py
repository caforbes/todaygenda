import datetime as dt

from config import get_settings
from db.connect import query_connect
from src.models import Daylist, Agenda, AgendaItem
from src.utils import next_midnight


SETTINGS = get_settings()
DB = query_connect(SETTINGS.database_url)


def temp_get_daylist() -> Daylist:
    """Get or create an unexpired daylist for today, for a placeholder user."""
    with DB.transaction():
        temp_user_id = DB.get_anon_user()["id"]
        active_daylist = DB.get_active_daylist(user_id=temp_user_id)

        if not active_daylist:
            DB.add_daylist(user_id=temp_user_id, expiry=next_midnight())
            active_daylist = DB.get_active_daylist(user_id=temp_user_id)

    return Daylist.model_validate(active_daylist)


def build_agenda(daylist: Daylist) -> Agenda:
    timestamp = dt.datetime.now().replace(second=0, microsecond=0)
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
        finish=timestamp,
        past_expiry=(timestamp > daylist.expiry),
    )
