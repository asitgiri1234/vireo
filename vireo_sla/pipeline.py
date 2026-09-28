"""End-to-end build used by the app and by tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from vireo_sla.clean import attach_ist, clean_csat, dedupe_tickets
from vireo_sla.load import load_pack
from vireo_sla.metrics import add_ownership, agent_totals, headline, weekly_by_agent, weekly_by_shift
from vireo_sla.roster import join_roster
from vireo_sla.sla import annotate_sla


def build_tickets(tickets_raw: pd.DataFrame, agents_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    tickets, dropped = dedupe_tickets(tickets_raw)
    tickets = attach_ist(tickets)
    tickets["csat"] = clean_csat(tickets["csat_score"], tickets["source_system"])
    tickets = annotate_sla(tickets)
    tickets = join_roster(tickets, agents_raw)
    unmatched = int(tickets["roster_shift"].isna().sum())
    tickets = add_ownership(tickets)
    audit = {
        "rows_in": int(len(tickets_raw)),
        "unique_tickets": int(len(tickets)),
        "duplicate_rows_dropped": int(dropped),
        "unmatched_roster": unmatched,
        "measurable": int(tickets["first_response_at"].notna().sum()),
        "breaches": int(tickets["breached"].sum()),
        "credits_inr": int(tickets["credit_inr"].sum()),
    }
    return tickets, audit


def summarise(tickets: pd.DataFrame, window: pd.DataFrame | None = None) -> dict:
    frame = tickets if window is None else window
    return {
        "headline": headline(frame),
        "weekly_shift": weekly_by_shift(frame),
        "weekly_agent": weekly_by_agent(frame),
        "agent_totals": agent_totals(frame),
    }


def build_from_disk(root: Path | None = None) -> tuple[pd.DataFrame, dict, dict[str, pd.DataFrame]]:
    pack = load_pack(root)
    tickets, audit = build_tickets(pack["tickets"], pack["agents"])
    return tickets, audit, pack
