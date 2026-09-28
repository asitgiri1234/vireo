"""Roll tickets up the way Neha asked: weekly, by agent, by shift."""

from __future__ import annotations

import pandas as pd

from vireo_sla.constants import CREDIT_INR
from vireo_sla.sla import created_in_roster_shift


def add_ownership(tickets: pd.DataFrame) -> pd.DataFrame:
    out = tickets.copy()
    own = created_in_roster_shift(out["create_hour_ist"], out["roster_shift"])
    out["own_shift"] = own.fillna(False)
    out["inherited"] = ~out["own_shift"]
    return out


def weekly_by_shift(tickets: pd.DataFrame) -> pd.DataFrame:
    cols = ["week_start", "roster_shift"]
    grouped = tickets.groupby(cols, dropna=False)
    rows = []
    for keys, frame in grouped:
        row = {
            "week_start": keys[0],
            "roster_shift": keys[1],
            "tickets": int(len(frame)),
            "breaches": int(frame["breached"].sum()),
            "inherited_breaches": int((frame["breached"] & frame["inherited"]).sum()),
            "own_breaches": int((frame["breached"] & frame["own_shift"]).sum()),
            "night_gap_breaches": int((frame["breached"] & frame["night_gap"]).sum()),
            "credits_inr": int(frame["credit_inr"].sum()),
        }
        row["breach_rate"] = row["breaches"] / row["tickets"] if row["tickets"] else None
        rows.append(row)
    out = pd.DataFrame(rows).sort_values(["week_start", "roster_shift"])
    return out.reset_index(drop=True)


def weekly_by_agent(tickets: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "week_start",
        "agent_id",
        "agent_name",
        "roster_shift",
        "roster_site",
        "roster_team",
    ]
    rows = []
    for keys, frame in tickets.groupby(cols, dropna=False):
        tickets_n = int(len(frame))
        breaches = int(frame["breached"].sum())
        own_tickets = int(frame["own_shift"].sum())
        own_breaches = int((frame["breached"] & frame["own_shift"]).sum())
        inherited_breaches = int((frame["breached"] & frame["inherited"]).sum())
        rows.append(
            {
                "week_start": keys[0],
                "agent_id": keys[1],
                "agent_name": keys[2],
                "roster_shift": keys[3],
                "roster_site": keys[4],
                "roster_team": keys[5],
                "tickets": tickets_n,
                "breaches": breaches,
                "inherited_breaches": inherited_breaches,
                "own_tickets": own_tickets,
                "own_breaches": own_breaches,
                "night_gap_breaches": int((frame["breached"] & frame["night_gap"]).sum()),
                "credits_inr": int(frame["credit_inr"].sum()),
                "breach_rate": breaches / tickets_n if tickets_n else None,
                "own_breach_rate": own_breaches / own_tickets if own_tickets else None,
            }
        )
    out = pd.DataFrame(rows).sort_values(
        ["week_start", "inherited_breaches", "breaches"], ascending=[True, False, False]
    )
    return out.reset_index(drop=True)


def agent_totals(tickets: pd.DataFrame) -> pd.DataFrame:
    cols = ["agent_id", "agent_name", "roster_shift", "roster_site", "roster_team"]
    rows = []
    for keys, frame in tickets.groupby(cols, dropna=False):
        tickets_n = int(len(frame))
        breaches = int(frame["breached"].sum())
        own_tickets = int(frame["own_shift"].sum())
        own_breaches = int((frame["breached"] & frame["own_shift"]).sum())
        inherited_breaches = int((frame["breached"] & frame["inherited"]).sum())
        rows.append(
            {
                "agent_id": keys[0],
                "agent_name": keys[1],
                "roster_shift": keys[2],
                "roster_site": keys[3],
                "roster_team": keys[4],
                "tickets": tickets_n,
                "breaches": breaches,
                "inherited_breaches": inherited_breaches,
                "own_tickets": own_tickets,
                "own_breaches": own_breaches,
                "night_gap_breaches": int((frame["breached"] & frame["night_gap"]).sum()),
                "credits_inr": int(frame["credit_inr"].sum()),
                "breach_rate": breaches / tickets_n if tickets_n else None,
                "own_breach_rate": own_breaches / own_tickets if own_tickets else None,
            }
        )
    out = pd.DataFrame(rows).sort_values("inherited_breaches", ascending=False)
    return out.reset_index(drop=True)


def headline(tickets: pd.DataFrame, target_rate: float = 0.15) -> dict:
    n = int(len(tickets))
    breaches = int(tickets["breached"].sum())
    rate = breaches / n if n else 0.0
    credits = int(tickets["credit_inr"].sum())
    target_breaches = int(round(target_rate * n))
    saved_breaches = max(breaches - target_breaches, 0)
    inherited = int((tickets["breached"] & tickets["inherited"]).sum())
    night_gap = int((tickets["breached"] & tickets["night_gap"]).sum())
    own = int((tickets["breached"] & tickets["own_shift"]).sum())
    return {
        "tickets": n,
        "breaches": breaches,
        "breach_rate": rate,
        "credits_inr": credits,
        "target_rate": target_rate,
        "target_breaches": target_breaches,
        "saving_inr": saved_breaches * CREDIT_INR,
        "inherited_breaches": inherited,
        "own_breaches": own,
        "night_gap_breaches": night_gap,
        "inherited_share": inherited / breaches if breaches else 0.0,
    }
