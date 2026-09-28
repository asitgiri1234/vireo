# Submission form — Vireo Audio, Support Tickets (Set D)

The pack we received did not include this file. The brief still requires it. Answers below.

## Who

- **Submitter:** Asit Giri (`asitgiri1234`)
- **Repo:** https://github.com/asitgiri1234/vireo
- **Window used:** built and pushed in this working session (well under the 5-hour cap)

## 1. Working tool

- **What to run:** `python -m pip install -r requirements.txt` then `python -m pytest` then `streamlit run app.py`
- **Starts from:** `README.md` on a clean machine
- **Stack:** Python, pandas, Streamlit, Altair, pytest
- **Data:** `data/tickets.csv`, `data/agents.csv` (other pack files included, not used in the report)

## 2. Business goal, as a number

**Cut first-response SLA breach from 25% to 15% on the current run-rate, worth about ₹80,000 a quarter in automatic ₹350 store credits.**

No new hires. Restore overnight chat coverage from the existing roster (night seats ended 29 June 2025).

Evidence: last 12 complete weeks ~25% miss; pre-29-June 2025 we were at 9–10%; Morning own-shift miss rate is already ~8%; night-created chat after the reshuffle misses ~100%.

## 3. How we know it works, and how often it does not

- **Unit tests** for SLA boundaries, timezone, dedup, June roster move, leftover vs own-shift.
- **Pack tests** locked to this export: 11,816 → 11,200 tickets, 616 duplicates, 0 unmatched roster, no Night-roster tickets after 29 Jun 2025, UTC-as-IST **flips** the guilty shift.
- **In the app:** “How we know this is right” tab repeats the traps.
- **It is wrong if** you quote headline miss % to a Morning agent without the leftover split (that is the helpdesk report, and it is what demoralises them).
- **It is silent on** CSAT, refunds, and the ~40 failed IVR transcripts (left in; they still have a first-response time).

On this pack, the arithmetic is either right or the tests fail. Interpretation is the remaining risk, not a 5% fudge factor on the rate.

## 4. Memo

`docs/memo-to-neha.md` — one page, to Neha, not technical.

## 5. Screen recording

Not in the repo. Record ≤3 minutes of the running app: prompts used, what changed between versions, what was thrown away. Phone recording of the screen is enough. No slides.

## 6. AI tools — honest account

**Used**

- Cursor (Composer / Auto) to write the pipeline, app, tests, and copy
- The same assistant to probe the CSVs (UTC vs IST, duplicates, June roster, credit run-rate)
- No model API inside the product. No OpenAI / Anthropic / Gemini key was billed for inference on tickets.

**Cost**

- Cursor subscription time already paid for. **Incremental model/API cost for this submission: ₹0.**
- No credits were provided in the pack; none were bought.

**Discarded**

- An LLM “ask the CSV” chat — it would guess; Neha needs counts she can take into a 1:1
- A CSAT dashboard — Priya’s thread, not the ask; legacy `0` would poison the average
- Refund / replacement leakage — policy has rupees, but it is not a first-response report
- A React + API build — would not finish inside the cap
- Ranking Morning agents by headline miss % with no leftover split — true to helpdesk, false to the situation
- Treating timestamps as IST because the helpdesk UI does — Sameer said the export is UTC
- “Hire night shift” — Arjun froze headcount; the June reshuffle was cost-neutral, so moving coverage back is the lever

**Prompts / versions (for the recording)**

1. First pass: “what are we building, what stack”
2. Probe the pack for breach %, credits, shift, duplicates, roster
3. Build the smallest tool that is the weekly report plus leftover split plus night-gap chart plus tests
4. Threw away chatbot, CSAT, hiring, and UTC-naive shift names

## Decisions

Written in `docs/decisions.md`. Short version: convert timezone, keep helpdesk attribution, split leftover vs own, join roster by date, keep helpdesk row on duplicate ids, 25% → 15% / ~₹80k a quarter, do not hire.

## Scope we ran out of on purpose

Orders, products, customers, Care+, transfer cost, repeat contacts, a pretty design system. A working weekly report beats a platform that does not start.
