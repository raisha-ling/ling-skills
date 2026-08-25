---
name: user-interview-prep
description: >-
  Build a dossier and a timed, ready-to-run script for a specific user ahead of a scheduled user
  interview, discovery call, churn call, or research session. Use whenever someone names a user
  they are about to talk to and wants to know what to ask: "I have a user interview at 4pm with
  <email>", "interview prep for this customer", "call with a user in an hour, what do we know",
  "research session with <user id>", or when handed a Calendly booking, a CRM contact, or a user
  id. Produces a live-use document — who they are, what they actually did, what we did to them,
  and a minute-by-minute script weighted to whatever makes this particular user worth the slot.
  Do NOT use for diagnosing an outage or deciding a bug's severity; that is incident work.
---

# User interview prep

Turn a bare email address into a document you can keep open during a live call.

Two halves, and both are required. **The dossier** — who this person is, what they actually did,
and what we did to them. **The script** — a timed plan whose weighting is derived from the dossier,
not from a template.

The whole point is that a generic "tell us what you love about the product" script wastes the slot.
The evidence tells you which 30 minutes to run.

## What this is not

Incident work and interview prep start the same way — pin an identity, sweep the same systems — and
diverge on output.

- **Incident triage** → a verdict. What broke, how broad, what severity, which repo. The reader is
  an engineer or a prioritization call.
- **This skill** → a conversation plan. The reader is a person, live, with a human on the other end.

If the ask is "what happened to this user", that is incident work. If the ask is "I'm talking to
this user at 4pm", it is this one. When a bug surfaces during prep — it often does — write it up
separately and route it; don't let it eat the interview prep.

## Tools this expects

Name what you have; the skill degrades gracefully. It was built against a support inbox/CRM
(HubSpot), product analytics (Amplitude), a payment processor (Stripe), a web-funnel platform
(Web2Wave), and a calendar. **Any equivalent works** — the method is "join across systems and read
the seams", not these vendors. Sources that fail or are missing get named in the output rather than
silently dropped.

## Canonical inputs

Read these from the workspace if they exist. Skip any that don't; the skill still works.

- `00-brain/customers.md` — personas, jobs-to-be-done, known pains. Place the user against a
  persona; say which, and say if they don't fit one.
- `00-brain/offers.md` — the price ladder, so you read their billing history correctly.
- Evidence sources and their gotchas: [`references/evidence-sweep.md`](references/evidence-sweep.md).
- Archetypes and time weighting: [`references/archetypes.md`](references/archetypes.md).

## Workflow

**0 — Grep the workspace first.** Someone may have already worked this case. One command, and it
has returned the whole answer before. See [`evidence-sweep.md` §0](references/evidence-sweep.md).

**1 — Pin identity, then check it isn't two people-shaped things.** Email → user id. Everything
downstream joins on that id — but **one person is not always one account**, and a second account is
the likeliest single explanation for "we fixed it and they say it's still broken." Run the
duplicate check in [`evidence-sweep.md`](references/evidence-sweep.md) before building the timeline.

**2 — Sweep the evidence.** Run the sources in
[`references/evidence-sweep.md`](references/evidence-sweep.md) **in parallel**. Do not stop at the
first source that answers; the story is almost always in the seam between two systems.

**3 — Reconstruct the timeline.** One table, UTC, one row per event, source named per row. Convert
to the user's local time in a note so their evening reads as an evening. Include their own words
from any support ticket verbatim — their phrasing is evidence.

**4 — Classify the archetype.** This decides the script weighting. See
[`references/archetypes.md`](references/archetypes.md). Do not skip to writing questions before
this is settled.

**5 — Write the dossier.** Numbers first, in tables. Lifetime usage minutes, sessions, lessons or
equivalent, days since last activity, net revenue. Their stated onboarding motivations quoted back
exactly — those are their words to us and they're gold in a call.

**6 — Write the timed script.** Minute ranges that sum to the slot length. Bold the verbatim asks;
leave probes unbolded as optional. Weight per archetype.

**7 — List the traps.** Every prep doc ends with what will go wrong in *this* call. Standing list
below, plus the case-specific ones.

**8 — List pre-call checks.** Anything that must be true before dialling — promised incentives
actually queued, tickets correctly categorised, account in the state you'll claim it's in.

**Always check that the meeting exists.** A booking bot assigning a slot in a chat channel is not
the same as a seat on the calendar. Verify the invite and the join link, and if the two disagree,
**lead the dossier with that** — a prep doc for a call that isn't happening is worse than no prep
doc, because it gets read as confirmation.

## Output

One file: `<research-area>/interviews/<YYYY-MM-DD>-<name-slug>.md`.

Required sections, in order:

1. **Read this first** — the single most important thing, in three bullets or fewer.
2. **Who they are** — table. Demographics, device, acquisition, language/product pair, stated motivations.
3. **What they actually did** — table. Engagement numbers, blunt.
4. **What actually happened** — the timeline, with sources per row.
5. **Anything we assumed on their behalf** — see below. Often the sharpest section.
6. **Defects this exposed** — if any. Marked as not yet independently reviewed.
7. **The script** — timed.
8. **Traps.**
9. **Verify before the call.**
10. **After the call** — where findings route.
11. **Sources** — every system queried, including the ones that returned nothing or failed.

## Always check: what did they actually ask for?

When a support ticket is in the history, compare **what the user asked for** against **what support
decided on their behalf**, then check whether the user ever confirmed.

Silence after a resolution email is not agreement. A user who asked for "a refund" and was given
"a refund for one of them, and you're still subscribed for a year" may or may not have wanted that —
and if they went dark afterwards, that ambiguity is a live interview question, not a closed ticket.

**If their last message is unanswered, that outranks everything else in the dossier.** A request we
have not replied to is owed an answer *before* the call, not during it.

This is a standing check because it is invisible unless you look for it, and it inverts the whole
framing of a call when it lands.

## Traps — carry these into every prep doc, then add case-specific ones

- **Incentive bias.** Users recruited through a support close-out email are often paid in free
  months. That biases them toward niceness. Counter it out loud in the opener: the critical stuff
  is more useful.
- **They may think it's a support call.** The interview invite often ships in the same email as the
  ticket resolution. Close the billing loop in the first 30 seconds or it eats the slot.
- **An unanswered message from them is worse than an open ticket.** Decide the answer in advance —
  a concession improvised live, for someone who has already been told "fixed", is how a second
  failure happens. Name the decision in the pre-call checks.
- **If a fix was claimed under the interviewer's own name and did not hold, put it in "Read this
  first."** They may quote it back. Owning it in one sentence costs nothing; deflecting it onto
  support loses the call.
- **Never reveal a defect you found.** Describing the bug converts an interview into an
  agreement-collection exercise. Ask what they *saw*.
- **Never quote their usage numbers at them.** "You only used it 44 minutes" ends the conversation.
  The number is for the interviewer.
- **Never defend the product.** Not once. Anger is data.
- **Don't infer tech literacy from age.** Check what the evidence says they actually did.
- **Silence is the tool.** Note it in the doc — five seconds before filling a gap.

## Definition of done

**Pass condition** — a prep doc ships only when all four are true, and each is checkable without
argument:

1. **Every number traces to a named system and a query that was actually run.** No estimate is
   presented as a count. A reader can pick any figure and see where it came from.
2. **The timed sections sum exactly to the slot length.** 30-minute slot, sections summing to 30.
3. **Every system touched appears in Sources — including the ones that returned nothing and the
   ones that failed.** A silent omission reads as "we checked everything" when it didn't.
4. **Every claim about what the user wanted is either a direct quote from them, or explicitly
   labelled as an assumption we made.**

**Golden example.** Input: an email address and a 30-minute slot tomorrow. Output: a dossier
showing the user cancelled their trial 8 seconds after a run of five lesson-starts that never
completed, restarted the app four times, then filed a bug naming the feature — with a script
weighted 40% to reconstructing that sequence from what they *saw*, and a trap block forbidding any
mention of the events themselves. Every timestamp carries its source; the calendar tool's failure
is named in Sources rather than omitted.

**Adversarial case.** Input: an email that resolves to no account, or an account with no events —
the user churned before analytics, or signed up with a different address. The skill must **say it
cannot build the dossier and name exactly which lookups returned empty**, then offer the one thing
that is still useful: a short unweighted discovery script plus the two identity questions that
resolve the mismatch on the call. It must **not** invent an archetype, infer engagement from the
absence of data, or pad the slot with generic feature questions. "No data" is a finding about our
systems, not a reason to guess.

## About

**Privilege level: draft-only.** Reads from the CRM, analytics, billing and calendar; writes one
local markdown file for a human to use. It sends nothing, replies to no ticket, and changes no
subscription. Any billing or support action it recommends is left for a person to take.

**Handle the output as confidential.** A prep doc contains real customer PII — email, location,
device, billing history, verbatim support messages. Keep it in the workspace. Do not publish it,
paste it into a shared document, or attach it to a ticket without the owner's explicit say-so.

Findings or defect numbers that leave the workspace — to leadership, an engineer, or an issue
tracker — should be independently reviewed first, and the doc marks them as unreviewed until they
are.
