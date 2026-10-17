"""Fetch solar storm records from NASA's DONKI space-weather database.

SEP = solar energetic particle event: a burst of fast protons from the Sun,
the radiation storms that matter for crew health. FLR = solar flare.
Endpoint: https://ccmc.gsfc.nasa.gov/DONKI-API/get/SEP (and /FLR). NASA moved
DONKI here on 30 Sep 2026; it needs no key and serves at most 60 days per call.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

BASE = "https://ccmc.gsfc.nasa.gov/DONKI-API/get/{kind}"
MAX_DAYS = 60
CACHE = Path(__file__).resolve().parent.parent / "data" / "donki"


def fetch_year(kind: str, year: int) -> list[dict]:
    """One calendar year of events. Past years are cached as JSON."""
    import json
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"{kind}_{year}.json"
    if path.exists() and year < date.today().year:
        return json.loads(path.read_text())
    start, end = date(year, 1, 1), min(date(year, 12, 31), date.today())
    events = []
    while start <= end:
        stop = min(start + timedelta(days=MAX_DAYS - 1), end)
        r = requests.get(BASE.format(kind=kind), timeout=60, params={
            "startDate": str(start), "endDate": str(stop)})
        r.raise_for_status()
        if r.text.strip():  # DONKI returns an empty body for no events
            events += r.json()
        start = stop + timedelta(days=1)
    path.write_text(json.dumps(events))
    return events


def sep_table(events: list[dict]) -> pd.DataFrame:
    rows = [{
        "sep_id": e.get("sepID"),
        "time": pd.to_datetime(e.get("eventTime"), utc=True),
        "instruments": ", ".join(i.get("displayName", "") for i in e.get("instruments") or []),
        "linked_events": ", ".join(l.get("activityID", "") for l in e.get("linkedEvents") or []),
    } for e in events]
    return pd.DataFrame(rows, columns=["sep_id", "time", "instruments", "linked_events"])


def flare_table(events: list[dict]) -> pd.DataFrame:
    rows = [{"flr_id": e.get("flrID"), "time": pd.to_datetime(e.get("peakTime") or e.get("beginTime"), utc=True),
             "class": e.get("classType")} for e in events]
    df = pd.DataFrame(rows, columns=["flr_id", "time", "class"])
    df["letter"] = df["class"].str[0]
    return df


def fetch_range(kind: str, first_year: int, last_year: int) -> list[dict]:
    out = []
    for y in range(first_year, last_year + 1):
        out += fetch_year(kind, y)
    return out
