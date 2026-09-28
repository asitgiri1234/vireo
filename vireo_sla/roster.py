"""Join tickets to the roster row that was in force on first-response date."""

from __future__ import annotations

import pandas as pd


def prepare_roster(agents: pd.DataFrame) -> pd.DataFrame:
    roster = agents.copy()
    roster["from_date"] = pd.to_datetime(roster["from_date"], errors="coerce")
    roster["to_date"] = pd.to_datetime(roster["to_date"], errors="coerce")
    roster["to_date"] = roster["to_date"].fillna(pd.Timestamp("2099-12-31"))
    roster = roster.rename(
        columns={
            "name": "agent_name",
            "site": "roster_site",
            "team": "roster_team",
            "shift": "roster_shift",
            "tier": "roster_tier",
        }
    )
    return roster


def join_roster(tickets: pd.DataFrame, agents: pd.DataFrame) -> pd.DataFrame:
    roster = prepare_roster(agents)
    work = tickets.copy()
    work["_fr_date"] = work["first_response_ist"].dt.tz_localize(None).dt.normalize()
    merged = work.merge(roster, on="agent_id", how="left")
    in_window = (merged["_fr_date"] >= merged["from_date"]) & (
        merged["_fr_date"] <= merged["to_date"]
    )
    matched = merged.loc[in_window].copy()
    # An agent should have one assignment on a given day. If a bad roster
    # row overlaps, keep the later from_date.
    matched = matched.sort_values(["ticket_id", "from_date"]).drop_duplicates(
        "ticket_id", keep="last"
    )
    keep_from_roster = [
        "ticket_id",
        "agent_name",
        "roster_site",
        "roster_team",
        "roster_shift",
        "roster_tier",
        "from_date",
        "to_date",
    ]
    out = work.merge(matched[keep_from_roster], on="ticket_id", how="left")
    out = out.drop(columns=["_fr_date"])
    return out
