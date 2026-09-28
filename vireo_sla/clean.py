"""Cleaning steps that the export needs before anyone looks at a rate.

Decisions (also in docs/decisions.md):
- API timestamps are UTC. Shift definitions are IST. Convert before
  assigning a shift. Duration itself does not depend on timezone.
- Keep the helpdesk row when the same ticket_id appears in both
  source systems (migration re-import).
- Join the roster on agent_id + first-response date, not on name.
- CSAT 0 on legacy rows is 'no response', not a score. We do not use
  CSAT in this report.
"""

from __future__ import annotations

import pandas as pd

from vireo_sla.constants import IST, PREFERRED_SOURCE


def parse_utc(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, utc=True, errors="coerce")


def dedupe_tickets(tickets: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Return unique tickets and the number of duplicate rows dropped."""
    before = len(tickets)
    unique_ids = tickets["ticket_id"].nunique()
    dropped = before - unique_ids
    preferred = tickets.copy()
    preferred["_keep"] = (preferred["source_system"] == PREFERRED_SOURCE).astype(int)
    preferred = (
        preferred.sort_values(["ticket_id", "_keep"])
        .drop_duplicates("ticket_id", keep="last")
        .drop(columns="_keep")
        .reset_index(drop=True)
    )
    return preferred, dropped


def clean_csat(series: pd.Series, source: pd.Series) -> pd.Series:
    """Blank and legacy 0 both mean no survey response."""
    del source  # documented so callers pass it; not needed for the rule
    out = pd.to_numeric(series, errors="coerce")
    return out.where(out != 0)


def attach_ist(tickets: pd.DataFrame) -> pd.DataFrame:
    out = tickets.copy()
    for col in ("created_at", "first_response_at", "resolved_at"):
        out[col] = parse_utc(out[col])
        ist_name = {
            "created_at": "created_ist",
            "first_response_at": "first_response_ist",
            "resolved_at": "resolved_ist",
        }[col]
        out[ist_name] = out[col].dt.tz_convert(IST)
    return out
