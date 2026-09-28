# Note to Neha Kulkarni

**From:** Kabir Nanda  
**Re:** Weekly first-response breaches — who to talk to, and what the number actually is  
**Date:** 28 September 2026

You asked for a weekly breach report by agent and by shift, with numbers you can take into the conversation. You have it. This note is only the conversation.

---

**The number.** On the last twelve complete weeks, **25% of tickets missed first response**. That is **₹1.8 lakh** in automatic ₹350 store credits in twelve weeks, about **₹2.0 lakh a quarter**. Arjun is right that the credit line is not what it was last summer. Priya is also right that month-to-month *now* it is flat: we have been sitting at this level since July 2025. CSAT is a different argument and this report does not mix it in.

**The goal.** Cut that 25% to **15%**. On today’s volume that is about **₹80,000 a quarter** back from the SLA credit line. Fifteen percent is not a slogan. Before 29 June 2025 we were at 9–10%. Volume is higher now, so I am not promising we return to nine. Fifteen is the number we can defend without hiring.

**Who looks guilty, and who is not.** Helpdesk already attributes every miss to the person who answered. On that report, Morning is the problem: roughly one in three of their tickets is a miss, and the names at the top of the list are Morning people in chat, logistics, billing, email and returns. That is the report that demoralises the morning chat team, and it is technically correct.

It is also the wrong conversation.

Nine in ten of Morning’s misses **opened before they came on shift**. Tickets that actually open during Morning hours miss about **8%** of the time — the same as Day. If you walk in with the helpdesk number you will be telling people off for a queue that formed at 11pm.

**What broke.** On 29 June 2025 the Indore night roster ended. Five night seats. Two chat agents (Tarun Mishra, Harpreet Deshpande) moved to Day. Three people have no later row. From July, **there is nobody rostered overnight**. Night-created tickets went from ~10% miss to ~80%. Night-created **chat** after that date misses **every time**: the customer waited a median seven hours against a fifteen-minute target, and Morning inherited the red. Chat is 15 minutes. It cannot survive a shift with no one in the chair.

That is also why credits jumped in Q3 last year and then stopped rising. We did not slowly get worse. We switched overnight coverage off.

**What to do, given Arjun will not hire.** Put overnight chat back with people already on the books. The June move was cost-neutral by Arjun’s own numbers; reversing the chat part of it is the same cost. Day does not need more people. Morning does not need a performance plan for leftover tickets. They need the pile to be smaller when they log in.

Email can often still hit eight hours if Morning clear it. Chat cannot. Cover chat at night first.

**How to use the tool in a 1:1.** Open the agent tab. You will see two miss counts: the helpdesk one, and the one that only counts tickets opened on that person’s shift. Talk to the second number. If you need a week-by-week sheet for a Team Lead, download the CSV. Default view is the last twelve complete weeks, Monday–Sunday IST.

**How we know this is not a timezone mess.** Sameer flagged it: the export is UTC, your shifts are IST. We converted before naming a shift. If we had not, Day would have looked like the problem. The tests in the repo fail if that conversion is skipped, if duplicate tickets from the migration are counted twice, or if a June mover is still labelled Night in July.

I am not sending you a league table of “worst agents”. I am sending you a way to have the conversation with the right people about the actual hole: overnight chat has been unstaffed for a year, and Morning has been wearing it.

Kabir
