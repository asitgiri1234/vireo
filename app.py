"""First-response breach report for Vireo support ops.

Run from the repo root:

    pip install -r requirements.txt
    streamlit run app.py
"""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from vireo_sla.constants import CREDIT_INR, NIGHT_COVERAGE_ENDED
from vireo_sla.metrics import headline
from vireo_sla.pipeline import build_from_disk, summarise

st.set_page_config(
    page_title="Vireo — first-response breaches",
    page_icon="🎧",
    layout="wide",
)


def inr(n: float | int) -> str:
    return f"₹{int(n):,}"


def pct(n: float | None) -> str:
    if n is None or pd.isna(n):
        return "—"
    return f"{100 * n:.1f}%"


@st.cache_data(show_spinner="Reading the export and applying the policy rules…")
def load_all() -> tuple[pd.DataFrame, dict]:
    tickets, audit, _pack = build_from_disk()
    return tickets, audit


def complete_week_starts(tickets: pd.DataFrame) -> list[pd.Timestamp]:
    last_day = tickets["created_ist"].dt.tz_localize(None).dt.normalize().max()
    starts = sorted(tickets["week_start"].dropna().unique())
    return [w for w in starts if (w + pd.Timedelta(days=6)) <= last_day]


def apply_filters(
    tickets: pd.DataFrame,
    weeks: tuple[pd.Timestamp, pd.Timestamp],
    shifts: list[str],
    sites: list[str],
) -> pd.DataFrame:
    lo, hi = weeks
    out = tickets[(tickets["week_start"] >= lo) & (tickets["week_start"] <= hi)]
    if shifts:
        out = out[out["roster_shift"].isin(shifts)]
    if sites:
        out = out[out["roster_site"].isin(sites)]
    return out


def rate_chart(weekly: pd.DataFrame, title: str) -> alt.Chart:
    data = weekly.copy()
    data["week"] = pd.to_datetime(data["week_start"]).dt.strftime("%d %b")
    data["rate_pct"] = data["breach_rate"] * 100
    return (
        alt.Chart(data)
        .mark_line(point=True)
        .encode(
            x=alt.X("week:N", title="Week starting", sort=None),
            y=alt.Y("rate_pct:Q", title="Breach %", scale=alt.Scale(zero=True)),
            color=alt.Color("roster_shift:N", title="Shift"),
            tooltip=["week", "roster_shift", "tickets", "breaches", "inherited_breaches", "credits_inr"],
        )
        .properties(height=280, title=title)
    )


def stacked_chart(weekly: pd.DataFrame) -> alt.Chart:
    long = weekly.melt(
        id_vars=["week_start", "roster_shift"],
        value_vars=["inherited_breaches", "own_breaches"],
        var_name="kind",
        value_name="breaches",
    )
    long["week"] = pd.to_datetime(long["week_start"]).dt.strftime("%d %b")
    long["kind"] = long["kind"].map(
        {"inherited_breaches": "Opened outside this shift", "own_breaches": "Opened on this shift"}
    )
    return (
        alt.Chart(long)
        .mark_bar()
        .encode(
            x=alt.X("week:N", title="Week starting", sort=None),
            y=alt.Y("breaches:Q", title="Breaches"),
            color=alt.Color("kind:N", title=""),
            tooltip=["week", "kind", "breaches"],
        )
        .properties(height=280, title="Morning looks red because of leftover tickets, not slow replies")
    )


tickets, audit = load_all()
week_starts = complete_week_starts(tickets)
all_weeks = sorted(tickets["week_start"].dropna().unique())
default_weeks = week_starts[-12:] if len(week_starts) >= 12 else all_weeks

st.title("First-response SLA — who is actually breaching")
st.caption(
    "Vireo Audio · timestamps converted UTC → IST · roster joined on the day of first response · "
    f"₹{CREDIT_INR} store credit per miss"
)

with st.sidebar:
    st.header("Window")
    st.write("Weeks are Monday–Sunday, IST. The last partial week is excluded from the default.")
    start = st.selectbox(
        "First week (Mon)",
        options=all_weeks,
        index=all_weeks.index(default_weeks[0]) if default_weeks[0] in all_weeks else 0,
        format_func=lambda d: pd.Timestamp(d).strftime("%d %b %Y"),
        help="Monday that starts the first week in the report. That whole week (Mon–Sun) is included.",
        key="first_week_mon",
    )
    # Last week can only be on or after First week — earlier Mondays are not offered.
    end_options = [w for w in all_weeks if pd.Timestamp(w) >= pd.Timestamp(start)]
    if not end_options:
        end_options = [start]
    preferred_end = default_weeks[-1] if default_weeks else end_options[-1]
    if preferred_end not in end_options:
        preferred_end = end_options[-1]
    if (
        "last_week_mon" not in st.session_state
        or st.session_state["last_week_mon"] not in end_options
    ):
        st.session_state["last_week_mon"] = preferred_end
    end = st.selectbox(
        "Last week (Mon)",
        options=end_options,
        format_func=lambda d: pd.Timestamp(d).strftime("%d %b %Y"),
        help="Only weeks on or after First week. That whole week (Mon–Sun) is included.",
        key="last_week_mon",
    )
    shifts = st.multiselect("Shift", ["Morning", "Day", "Night"], default=[])
    sites = st.multiselect("Site", ["Bengaluru", "Indore"], default=[])
    st.divider()
    st.markdown(
        f"**Do not hire.** Headcount is frozen until Q4. "
        f"Night roster ended **{NIGHT_COVERAGE_ENDED}**. "
        "The two Indore chat agents who moved Night → Day are still on the books."
    )

window = apply_filters(tickets, (start, end), shifts, sites)
if window.empty:
    st.warning("No tickets in this window.")
    st.stop()

summary = summarise(tickets, window)
h = summary["headline"]
# Scale a 12-week window to a quarter (~13 weeks) when the selected span is ~12 weeks.
span_weeks = max(int(round((pd.Timestamp(end) - pd.Timestamp(start)).days / 7)) + 1, 1)
quarter_factor = 13 / span_weeks if span_weeks else 1
quarter_saving = int(h["saving_inr"] * quarter_factor)
quarter_credits = int(h["credits_inr"] * quarter_factor)

st.info(
    f"**Goal:** cut first-response breach from **{pct(h['breach_rate'])} to 15%** "
    f"by covering overnight chat with people already on the roster. "
    f"On this window that is about **{inr(h['saving_inr'])}**, "
    f"**~{inr(quarter_saving)} a quarter** in automatic store credits. "
    f"Run-rate on the SLA credit line is ~{inr(quarter_credits)} a quarter."
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Tickets", f"{h['tickets']:,}")
c2.metric("Breaches", f"{h['breaches']:,}", delta=pct(h["breach_rate"]), delta_color="inverse")
c3.metric("SLA credits", inr(h["credits_inr"]))
c4.metric("Opened off-shift", f"{h['inherited_breaches']:,}", delta=pct(h["inherited_share"]))
c5.metric("Night-gap breaches", f"{h['night_gap_breaches']:,}")

tab_week, tab_agent, tab_gap, tab_qa = st.tabs(
    ["Weekly by shift", "Weekly by agent", "The night gap", "How we know this is right"]
)

with tab_week:
    st.subheader("The report Neha asked for")
    st.write(
        "Breach % by the **resolving agent's rostered shift** that week. "
        "Morning will dominate. Open the next tab before you walk into the 1:1."
    )
    weekly = summary["weekly_shift"]
    st.altair_chart(rate_chart(weekly, "Breach rate by shift"), use_container_width=True)
    morning = window[window["roster_shift"] == "Morning"]
    if not morning.empty:
        tmp = morning.copy()
        tmp["inherited_breaches"] = tmp["breached"] & tmp["inherited"]
        tmp["own_breaches"] = tmp["breached"] & tmp["own_shift"]
        m_week = tmp.groupby("week_start", as_index=False)[["inherited_breaches", "own_breaches"]].sum()
        m_week["roster_shift"] = "Morning"
        st.altair_chart(stacked_chart(m_week), use_container_width=True)
    show = weekly.copy()
    show["week_start"] = pd.to_datetime(show["week_start"]).dt.strftime("%Y-%m-%d")
    show["breach_rate"] = show["breach_rate"].map(lambda x: None if pd.isna(x) else round(100 * x, 1))
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.download_button(
        "Download weekly-by-shift CSV",
        show.to_csv(index=False).encode("utf-8"),
        file_name="weekly_by_shift.csv",
        mime="text/csv",
    )

with tab_agent:
    st.subheader("Who to talk to — and what to say")
    st.write(
        "Helpdesk attributes a miss to the **resolving agent**. That is the number they already have. "
        "The extra columns are the conversation: how many of those misses were tickets that opened "
        "**before this person came on shift**, versus tickets they actually owned."
    )
    sort_by = st.radio(
        "Sort agents by",
        ["Leftover breaches (default)", "Own-shift breach rate", "Total breaches"],
        horizontal=True,
    )
    agents = summary["agent_totals"].copy()
    if sort_by.startswith("Own-shift"):
        agents = agents.sort_values("own_breach_rate", ascending=False, na_position="last")
    elif sort_by.startswith("Total"):
        agents = agents.sort_values("breaches", ascending=False)
    else:
        agents = agents.sort_values("inherited_breaches", ascending=False)
    view = agents.copy()
    view["breach_rate"] = view["breach_rate"].map(lambda x: None if x is None or pd.isna(x) else round(100 * x, 1))
    view["own_breach_rate"] = view["own_breach_rate"].map(
        lambda x: None if x is None or pd.isna(x) else round(100 * x, 1)
    )
    st.dataframe(
        view.rename(
            columns={
                "agent_name": "agent",
                "roster_shift": "shift",
                "roster_site": "site",
                "roster_team": "team",
                "inherited_breaches": "leftover_breaches",
                "own_breaches": "own_shift_breaches",
                "own_breach_rate": "own_shift_breach_%",
                "breach_rate": "headline_breach_%",
                "credits_inr": "credits_₹",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
    names = ["—"] + sorted(agents["agent_name"].dropna().unique().tolist())
    picked = st.selectbox("Draft the 1:1 from the numbers", names)
    if picked != "—":
        row = agents[agents["agent_name"] == picked].iloc[0]
        leftover = int(row["inherited_breaches"])
        own_b = int(row["own_breaches"])
        st.success(
            f"**{picked}** ({row['roster_site']}, {row['roster_shift']}, {row['roster_team']}). "
            f"{int(row['breaches'])} misses on {int(row['tickets'])} tickets "
            f"({pct(row['breach_rate'])} — that is the helpdesk number). "
            f"**{leftover} of those misses opened before they came on shift.** "
            f"On tickets that opened during their shift: {int(row['own_tickets'])} tickets, "
            f"{own_b} misses ({pct(row['own_breach_rate'])}). "
            f"Credits on their attributed tickets: {inr(row['credits_inr'])}."
        )
    weekly_a = summary["weekly_agent"].copy()
    weekly_a["week_start"] = pd.to_datetime(weekly_a["week_start"]).dt.strftime("%Y-%m-%d")
    st.download_button(
        "Download weekly-by-agent CSV",
        weekly_a.to_csv(index=False).encode("utf-8"),
        file_name="weekly_by_agent.csv",
        mime="text/csv",
    )
    with st.expander("Week-by-week agent table"):
        st.dataframe(weekly_a, use_container_width=True, hide_index=True)

with tab_gap:
    st.subheader("Overnight chat has had no one on the roster since 29 June 2025")
    st.write(
        "Five Indore night seats ended that day. Two chat agents moved to Day. "
        "Three people have no later roster row. After that, every night-created chat "
        "waits for Morning — median wait ~7 hours against a 15-minute target."
    )
    night = tickets[tickets["create_shift"] == "Night"].copy()
    night["month"] = night["created_ist"].dt.tz_localize(None).dt.to_period("M").astype(str)
    by_month = (
        night.groupby("month", as_index=False)
        .agg(tickets=("ticket_id", "count"), breaches=("breached", "sum"))
    )
    by_month["breach_pct"] = 100 * by_month["breaches"] / by_month["tickets"]
    line = (
        alt.Chart(by_month)
        .mark_line(point=True)
        .encode(
            x=alt.X("month:N", title="Month", sort=None),
            y=alt.Y("breach_pct:Q", title="Night-created breach %"),
            tooltip=["month", "tickets", "breaches", "breach_pct"],
        )
        .properties(height=280, title="Night-created tickets: breach rate before and after the reshuffle")
    )
    st.altair_chart(line, use_container_width=True)

    in_window_night = window[window["create_shift"] == "Night"]
    chat_social = in_window_night[in_window_night["channel"].isin(["chat", "social"])]
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Night-created tickets in window", f"{len(in_window_night):,}")
    col_b.metric(
        "Of which chat + social",
        f"{len(chat_social):,}",
        delta=f"{int(chat_social['breached'].sum())} missed",
        delta_color="inverse",
    )
    col_c.metric(
        "Chat + social night miss rate",
        pct(chat_social["breached"].mean() if len(chat_social) else 0),
    )
    st.write(
        "Restore overnight chat with **people already employed** (Tarun Mishra and "
        "Harpreet Deshpande were Night until 29 June, then Day). That does not add headcount. "
        "It takes the leftover pile off Morning before anyone opens the queue."
    )

with tab_qa:
    st.subheader("How we know the numbers are right")
    st.write(
        "The export lies in a few documented ways. We handle each one, then check that "
        "the handling actually happened."
    )
    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows in the export", f"{audit['rows_in']:,}")
    q2.metric("Duplicate rows dropped", f"{audit['duplicate_rows_dropped']:,}")
    q3.metric("Unmatched to roster", f"{audit['unmatched_roster']:,}")
    q4.metric("Unique tickets", f"{audit['unique_tickets']:,}")

    st.markdown(
        """
**Traps in this pack, and what we did**

| Trap | What we did | How you can see it |
| --- | --- | --- |
| API timestamps are UTC; shifts are IST | Convert before naming a shift | Treating UTC as IST makes **Day** look like the problem and Night look fine. The opposite is true. |
| 616 tickets appear twice (helpdesk + legacy) | Keep the helpdesk row | Duplicate rows dropped, above |
| Roster is one row per assignment; people moved in June | Join on agent id + first-response **date** | Night-roster tickets fall to zero after 29 Jun 2025 |
| Helpdesk attributes the miss to whoever resolved it | Keep that, and split leftover vs own-shift | Morning headline ~32%, own-shift ~8% |
| Legacy CSAT uses 0 for no response | We do not use CSAT in this report | Out of scope — Priya's point, not Neha's ask |
| Failed IVR transcripts (~40) | Left in | They still have a first-response time; dropping them does not move the rate |

**Gold checks** (also in `tests/`): a chat that waited 16 minutes is a miss; 15 minutes is not. A ticket created at 01:00 IST is Night, even though the UTC clock says 19:30. Equal-to-SLA is on time (policy: *later than* the target).
        """
    )
    st.markdown(
        f"On the **full** history, not just this window: "
        f"{audit['breaches']:,} misses, {inr(audit['credits_inr'])} in credits, "
        f"{audit['unique_tickets']:,} tickets after de-dupe."
    )
    st.caption(
        "Wrong on purpose if: a ticket has no first_response_at (none in this export); "
        "or an agent is missing from the roster on that day (none after the date join). "
        "Wrong in interpretation if you quote headline breach % to a Morning agent without the leftover split."
    )

st.divider()
st.caption(
    "Policy v3.2 · first response = first human reply · chat 15m · voice 2h · social 4h · email 8h · "
    "₹350 credit per miss · headcount frozen until Q4"
)
