import datetime as dt

from src.models import Daylist, Agenda, AgendaItem


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
