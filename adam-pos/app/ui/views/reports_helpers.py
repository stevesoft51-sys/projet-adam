"""Helpers pour la vue rapports."""
from datetime import datetime

from ...services import period_range


def period_label(period: str, state=None) -> str:
    start, end = period_range(period)
    fmt_d = "%d/%m/%Y"
    tr = (lambda k, **kw: state.tr(k, **kw)) if state else (lambda k, **kw: k)
    if period == "Jour":
        return tr("dash.period.today") + f" · {start.strftime(fmt_d)}"
    if period == "Hier":
        return tr("dash.period.yesterday") + f" · {start.strftime(fmt_d)}"
    if period == "Semaine":
        monday = (datetime.now() - __import__("datetime").timedelta(
            days=datetime.now().weekday()))
        end_week = monday + __import__("datetime").timedelta(days=6)
        return (tr("dash.period.current_week")
                + f" · {tr('dash.period.from')} {start.strftime(fmt_d)} "
                f"{tr('dash.period.to')} {end_week.strftime(fmt_d)}")
    if period == "Mois":
        return tr("dash.period.month") + f" {start.strftime('%B %Y').capitalize()}"
    return tr("dash.period.year") + f" {start.year}"
