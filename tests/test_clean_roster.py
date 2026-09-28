"""Dedup, CSAT zero, and roster date-join."""

import pandas as pd

from vireo_sla.clean import clean_csat, dedupe_tickets
from vireo_sla.pipeline import build_tickets
from vireo_sla.roster import join_roster
from vireo_sla.clean import attach_ist


def test_dedupe_keeps_helpdesk_row():
    raw = pd.DataFrame(
        {
            "ticket_id": ["TK-1", "TK-1", "TK-2"],
            "source_system": ["legacy_fd", "helpdesk", "legacy_fd"],
            "channel": ["chat", "chat", "email"],
        }
    )
    out, dropped = dedupe_tickets(raw)
    assert dropped == 1
    assert len(out) == 2
    assert out.set_index("ticket_id").loc["TK-1", "source_system"] == "helpdesk"


def test_legacy_csat_zero_is_missing():
    scores = pd.Series([5, 0, None, 3])
    source = pd.Series(["helpdesk", "legacy_fd", "helpdesk", "legacy_fd"])
    out = clean_csat(scores, source)
    assert list(out.isna()) == [False, True, True, False]
    assert out.dropna().tolist() == [5, 3]


def test_june_move_uses_the_new_shift_after_the_from_date():
    tickets = pd.DataFrame(
        {
            "ticket_id": ["A", "B"],
            "agent_id": ["A3002", "A3002"],
            "created_at": ["2025-06-28 20:00:00", "2025-07-01 20:00:00"],
            "first_response_at": ["2025-06-28 20:10:00", "2025-07-01 20:10:00"],
            "resolved_at": ["2025-06-28 20:20:00", "2025-07-01 20:20:00"],
            "channel": ["chat", "chat"],
        }
    )
    tickets = attach_ist(tickets)
    agents = pd.DataFrame(
        {
            "agent_id": ["A3002", "A3002"],
            "name": ["Tarun Mishra", "Tarun Mishra"],
            "site": ["Indore", "Indore"],
            "team": ["Chat Frontline", "Chat Frontline"],
            "shift": ["Night", "Day"],
            "tier": [1, 1],
            "from_date": ["2023-02-12", "2025-06-30"],
            "to_date": ["2025-06-29", None],
        }
    )
    joined = join_roster(tickets, agents)
    assert joined.set_index("ticket_id").loc["A", "roster_shift"] == "Night"
    assert joined.set_index("ticket_id").loc["B", "roster_shift"] == "Day"


def test_pipeline_flags_night_gap_after_coverage_ends():
    tickets = pd.DataFrame(
        {
            "ticket_id": ["N1"],
            "created_at": ["2025-07-02 18:30:00"],  # 00:00 IST the next day — Night
            "first_response_at": ["2025-07-03 01:00:00"],  # 06:30 IST Morning
            "resolved_at": ["2025-07-03 01:20:00"],
            "status": ["resolved"],
            "channel": ["chat"],
            "agent_id": ["A3005"],
            "source_system": ["helpdesk"],
            "csat_score": [4],
        }
    )
    agents = pd.DataFrame(
        {
            "agent_id": ["A3005"],
            "name": ["Sameer Joshi"],
            "site": ["Bengaluru"],
            "team": ["Chat Frontline"],
            "shift": ["Morning"],
            "tier": [1],
            "from_date": ["2021-07-28"],
            "to_date": [None],
        }
    )
    built, audit = build_tickets(tickets, agents)
    assert audit["unique_tickets"] == 1
    assert bool(built.loc[0, "breached"]) is True
    assert bool(built.loc[0, "night_gap"]) is True
    assert bool(built.loc[0, "inherited"]) is True
    assert built.loc[0, "roster_shift"] == "Morning"
    assert built.loc[0, "credit_inr"] == 350
