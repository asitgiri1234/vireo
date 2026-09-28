"""SLA boundary and timezone tests. No CSV required."""

from datetime import datetime

import pandas as pd

from vireo_sla.constants import IST, UTC
from vireo_sla.sla import created_in_roster_shift, hour_to_shift, is_breached, sla_minutes_for, wait_minutes


def _utc(*args):
    return pd.Timestamp(datetime(*args), tz=UTC)


def test_chat_16_minutes_is_a_breach():
    created = pd.Series([_utc(2026, 1, 1, 4, 0)])
    first = pd.Series([_utc(2026, 1, 1, 4, 16)])
    wait = wait_minutes(created, first)
    sla = sla_minutes_for(pd.Series(["chat"]))
    assert wait.iloc[0] == 16
    assert bool(is_breached(wait, sla).iloc[0]) is True


def test_chat_15_minutes_is_on_time():
    created = pd.Series([_utc(2026, 1, 1, 4, 0)])
    first = pd.Series([_utc(2026, 1, 1, 4, 15)])
    wait = wait_minutes(created, first)
    sla = sla_minutes_for(pd.Series(["chat"]))
    assert wait.iloc[0] == 15
    assert bool(is_breached(wait, sla).iloc[0]) is False


def test_email_8_hours_plus_one_minute_breaches():
    created = pd.Series([_utc(2026, 1, 1, 0, 0)])
    first = pd.Series([_utc(2026, 1, 1, 8, 1)])
    wait = wait_minutes(created, first)
    sla = sla_minutes_for(pd.Series(["email"]))
    assert bool(is_breached(wait, sla).iloc[0]) is True


def test_voice_exactly_two_hours_is_on_time():
    created = pd.Series([_utc(2026, 1, 1, 0, 0)])
    first = pd.Series([_utc(2026, 1, 1, 2, 0)])
    sla = sla_minutes_for(pd.Series(["voice"]))
    assert bool(is_breached(wait_minutes(created, first), sla).iloc[0]) is False


def test_duration_does_not_depend_on_timezone():
    created = pd.Series([_utc(2026, 6, 1, 18, 30)])
    first = pd.Series([_utc(2026, 6, 1, 18, 50)])
    wait_utc = wait_minutes(created, first)
    wait_ist = wait_minutes(
        created.dt.tz_convert(IST),
        first.dt.tz_convert(IST),
    )
    assert wait_utc.iloc[0] == wait_ist.iloc[0] == 20


def test_utc_0100_is_ist_morning_not_night():
    # 01:00 UTC = 06:30 IST → Morning. Treating the UTC hour as IST would call it Night.
    ts = pd.Series([_utc(2026, 1, 15, 1, 0)]).dt.tz_convert(IST)
    assert hour_to_shift(ts.dt.hour).iloc[0] == "Morning"
    assert hour_to_shift(pd.Series([1])).iloc[0] == "Night"


def test_ist_0100_is_night():
    ts = pd.Series([pd.Timestamp("2026-01-15 01:00", tz=IST)])
    assert hour_to_shift(ts.dt.hour).iloc[0] == "Night"


def test_inherited_when_morning_agent_answers_overnight_ticket():
    created_hour = pd.Series([1, 10, 15])
    roster = pd.Series(["Morning", "Morning", "Morning"])
    own = created_in_roster_shift(created_hour, roster)
    assert list(own) == [False, True, False]


def test_night_shift_owns_late_evening_and_early_morning():
    created_hour = pd.Series([22, 3, 7, 14])
    roster = pd.Series(["Night"] * 4)
    own = created_in_roster_shift(created_hour, roster)
    assert list(own) == [True, True, False, False]
