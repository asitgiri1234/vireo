"""Checks against the real pack. Skips if data/tickets.csv is missing."""

from pathlib import Path

import pandas as pd
import pytest

from vireo_sla.constants import NIGHT_COVERAGE_ENDED
from vireo_sla.pipeline import build_from_disk

DATA = Path(__file__).resolve().parent.parent / "data" / "tickets.csv"


@pytest.mark.skipif(not DATA.exists(), reason="pack not present")
def test_pack_dedupes_to_11200_and_joins_everyone():
    tickets, audit, _ = build_from_disk()
    assert audit["rows_in"] == 11816
    assert audit["duplicate_rows_dropped"] == 616
    assert audit["unique_tickets"] == 11200
    assert audit["unmatched_roster"] == 0
    assert tickets["ticket_id"].is_unique
    assert 0.20 < tickets["breached"].mean() < 0.24
    assert audit["credits_inr"] == int(tickets["breached"].sum()) * 350


@pytest.mark.skipif(not DATA.exists(), reason="pack not present")
def test_night_roster_is_empty_after_the_reshuffle():
    tickets, _audit, _ = build_from_disk()
    ended = pd.Timestamp(NIGHT_COVERAGE_ENDED)
    fr_day = tickets["first_response_ist"].dt.tz_localize(None).dt.normalize()
    later = tickets[(fr_day > ended) & (tickets["roster_shift"] == "Night")]
    assert later.empty


@pytest.mark.skipif(not DATA.exists(), reason="pack not present")
def test_morning_headline_is_mostly_leftovers():
    tickets, _audit, _ = build_from_disk()
    morning = tickets[tickets["roster_shift"] == "Morning"]
    share = (morning["breached"] & morning["inherited"]).sum() / morning["breached"].sum()
    own_rate = morning.loc[morning["own_shift"], "breached"].mean()
    assert share > 0.85
    assert own_rate < 0.12


@pytest.mark.skipif(not DATA.exists(), reason="pack not present")
def test_treating_utc_hour_as_ist_flips_the_story():
    tickets, _audit, _ = build_from_disk()
    utc_hour = tickets["created_at"].dt.hour
    ist_hour = tickets["created_ist"].dt.hour
    from vireo_sla.sla import hour_to_shift

    fake = hour_to_shift(utc_hour)
    real = hour_to_shift(ist_hour)
    fake_night_rate = tickets.loc[fake == "Night", "breached"].mean()
    real_night_rate = tickets.loc[real == "Night", "breached"].mean()
    # The trap: UTC-as-IST makes Night look calm. Reality: Night-created is the fire.
    assert fake_night_rate < 0.20
    assert real_night_rate > 0.55


@pytest.mark.skipif(not DATA.exists(), reason="pack not present")
def test_last_12_complete_weeks_goal_math():
    tickets, _audit, _ = build_from_disk()
    last_day = tickets["created_ist"].dt.tz_localize(None).dt.normalize().max()
    starts = sorted(tickets["week_start"].dropna().unique())
    complete = [w for w in starts if (w + pd.Timedelta(days=6)) <= last_day][-12:]
    window = tickets[tickets["week_start"].isin(complete)]
    rate = window["breached"].mean()
    n = len(window)
    breaches = int(window["breached"].sum())
    target = int(round(0.15 * n))
    saving = (breaches - target) * 350
    assert 0.23 < rate < 0.28
    # ~₹80k a quarter ≈ this 12-week saving scaled by 13/12, give or take volume.
    quarter = saving * (13 / 12)
    assert 50_000 < quarter < 120_000
