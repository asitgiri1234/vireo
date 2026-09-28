# Decisions we made because nobody was free to ask

The brief is an email, not a spec. These are the calls.

## 1. Shift names after converting UTC → IST

Sameer: the API export is UTC. Policy: shifts are IST. Duration does not care. **Which shift a ticket belongs to does.**

If we skip the conversion, Day looks like the problem and Night looks fine. After conversion, night-created tickets are ~64% miss; Day and Morning creates are ~9–10%. We convert. There is a test that the ranking flips without it.

## 2. Attribute the miss to the resolving agent, then split leftover vs own

Policy §3: helpdesk reports the miss against the resolving agent. Neha wants that number in the room. We keep it.

We will not walk into a Morning 1:1 with only that number. Priya said the morning chat team open the day to a wall of red. So every miss is also tagged:

- **own-shift** — opened during the resolving agent's rostered hours that day
- **leftover / inherited** — opened outside those hours (almost all of these are overnight)

Morning headline miss rate is ~32%. On tickets that opened during Morning hours it is ~8%. ~90% of Morning's attributed misses are leftovers.

## 3. Join the roster on first-response **date**, not on name, not on "current" shift

`agent_id` is the key. People move. Tarun Mishra and Harpreet Deshpande were Night until 29 Jun 2025 and Day from 30 Jun. A ticket they answered in July is a Day ticket. Using the name, or the latest row only, would smear the reshuffle.

## 4. Duplicate `ticket_id`: keep helpdesk, drop legacy

616 tickets appear in both systems. Sameer flagged the re-import. We keep `source_system = helpdesk`. Dropping 616 rows from 11,816 does not change the story; double-counting would.

## 5. Week = Monday–Sunday IST, clock starts at `created_at`

Neha plans weeks, not UTC days. SLA clock starts when the ticket is created, so the week is the create week, not the resolve week. The last partial week in the export is dropped from the default window so a stub Wednesday does not look like a miracle.

## 6. Equal to the SLA is on time

Policy: "later than the target". Chat at 15:00 is on time; 15:01 is a miss.

## 7. Business goal is 25% → 15%, ~₹80,000 a quarter

Last 12 complete weeks sit at ~25% miss. 15% is above the pre-reshuffle 9–10% (volume is higher now; we are not promising a time machine). The rupee figure is missed tickets avoided × ₹350, scaled 12 weeks → 13-week quarter. It is **SLA credits only**. We did not price CSAT, repeats, or brand.

The lever we name is overnight chat coverage from the **existing** roster. We do not recommend hiring. Arjun froze headcount. The June move was cost-neutral; putting two chat agents back on Night is the same cost.

## 8. What 15% does *not* assume

It does not assume Night email is staffed (8-hour email target can often be hit by Morning). It does not assume we touch Day, which is already ~8%. It does assume overnight **chat** (15-minute target) is no longer left on the floor until 06:00.

## 9. Out of scope

CSAT, refunds, replacements, transfer cost, Care+, product defects, a chatbot. Failed IVR transcripts stay in: they still have a first-response timestamp and there are ~40 of them.

## 10. "Wrong" will look like

Quoting headline miss % to a Morning agent without the leftover split. That is the report they already get, and it is why they are demoralised.
