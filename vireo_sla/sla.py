"""First-response SLA, shift windows, inherited vs own-shift."""

from __future__ import annotations

import pandas as pd

from vireo_sla.constants import CREDIT_INR, NIGHT_COVERAGE_ENDED, SLA_MINUTES


def sla_minutes_for(channel: pd.Series) -> pd.Series:
    return channel.map(SLA_MINUTES)


def wait_minutes(created_utc: pd.Series, first_response_utc: pd.Series) -> pd.Series:
    return (first_response_utc - created_utc).dt.total_seconds() / 60.0


def is_breached(wait_min: pd.Series, sla_min: pd.Series) -> pd.Series:
    """Policy: later than the target. Equal to the target is on time."""
    measurable = wait_min.notna() & sla_min.notna()
    return measurable & (wait_min > sla_min)


def hour_to_shift(hour: pd.Series) -> pd.Series:
    out = pd.Series("Night", index=hour.index)
    out[(hour >= 6) & (hour < 14)] = "Morning"
    out[(hour >= 14) & (hour < 22)] = "Day"
    return out


def created_in_roster_shift(created_hour: pd.Series, roster_shift: pd.Series) -> pd.Series:
    """True when the ticket was opened during the resolving agent's shift."""
    morning = (roster_shift == "Morning") & (created_hour >= 6) & (created_hour < 14)
    day = (roster_shift == "Day") & (created_hour >= 14) & (created_hour < 22)
    night = (roster_shift == "Night") & ((created_hour >= 22) | (created_hour < 6))
    return morning | day | night


def iso_week_start(ist_timestamps: pd.Series) -> pd.Series:
    naive = ist_timestamps.dt.tz_localize(None)
    # Monday as week start, matching how Neha plans 1:1s.
    return naive.dt.normalize() - pd.to_timedelta(naive.dt.dayofweek, unit="D")


def annotate_sla(tickets: pd.DataFrame) -> pd.DataFrame:
    out = tickets.copy()
    out["sla_minutes"] = sla_minutes_for(out["channel"])
    out["wait_minutes"] = wait_minutes(out["created_at"], out["first_response_at"])
    out["breached"] = is_breached(out["wait_minutes"], out["sla_minutes"])
    out["credit_inr"] = out["breached"].astype(int) * CREDIT_INR
    out["create_hour_ist"] = out["created_ist"].dt.hour
    out["fr_hour_ist"] = out["first_response_ist"].dt.hour
    out["create_shift"] = hour_to_shift(out["create_hour_ist"])
    out["fr_shift"] = hour_to_shift(out["fr_hour_ist"])
    out["week_start"] = iso_week_start(out["created_ist"])
    ended = pd.Timestamp(NIGHT_COVERAGE_ENDED)
    created_day = out["created_ist"].dt.tz_localize(None).dt.normalize()
    out["night_gap"] = (out["create_shift"] == "Night") & (created_day > ended)
    return out
