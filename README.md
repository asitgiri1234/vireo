# Vireo Audio — first-response breach report

A small local tool for Neha Kulkarni: **which agents and which shifts miss first-response SLA, weekly**, with the leftover overnight pile split out so Morning is not blamed for tickets that waited all night.

It starts from this README on a clean machine. No cloud, no API keys.

## What it is for

Cut first-response breach from **~25% to 15%** on the current run-rate, worth about **₹80,000 a quarter** in automatic ₹350 store credits. Headcount is frozen: the lever is restoring overnight chat coverage with people already on the roster. Night seats ended on **29 June 2025**.

## Run it

Python 3.11+ (tested on 3.13).

```bash
cd vireo
python -m pip install -r requirements.txt
python -m pytest
streamlit run app.py
```

Windows, same commands in PowerShell from this folder.

The app reads `data/tickets.csv` and `data/agents.csv`. Leave those files where they are.

## What you will see

1. **Weekly by shift** — the report that was asked for.
2. **Weekly by agent** — helpdesk's attributed miss count, plus leftover vs own-shift. Use this in the 1:1.
3. **The night gap** — breach rate on night-created tickets before and after the Indore reshuffle.
4. **How we know this is right** — traps in the export and the checks that caught them.

CSV downloads sit under the tables.

## How we know the numbers are right

`python -m pytest` runs:

- SLA boundaries (15 minutes on time, 16 a miss; equal-to-target is on time)
- UTC vs IST shift naming (treating UTC as IST **flips** who looks guilty)
- Duplicate ticket_ids keep the helpdesk row
- June roster move: same `agent_id`, new shift after `from_date`
- Against the real pack: 11,816 rows → 11,200 tickets, 616 duplicates dropped, 0 unmatched roster rows, no Night-roster tickets after 29 Jun 2025, Morning's misses are >85% leftovers

On this pack the tests are not "mostly right". They fail if the story changes.

## What we left out

On purpose, because five hours does not fit a support-wide review:

- CSAT (Priya's point; legacy `0` means no response, not a zero score)
- Refunds, replacements, transfers, Care+
- Hiring recommendations (frozen until Q4)
- An LLM sitting on the CSV (it would guess; the credits are arithmetic)

Decisions are in `docs/decisions.md`. The one-page note to Neha is `docs/memo-to-neha.md`.

## Pack

Original export lives in `data/`. Column dictionary is `data/README.txt`. Policy is `data/support-policy.pdf`. Earlier email thread is `data/email-thread.txt`.
