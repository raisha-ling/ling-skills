# Evidence sweep — sources, calls, and gotchas

Run these **in parallel**. Each one has burned time before; the gotchas are the point of this file.

Identity join key: the same user id should appear as the CRM contact property, the analytics
`userId`, the crash-reporter `user.id`, and the database document key. Confirm that before joining
anything — and see "One person is not always one account" below, because the assumption fails more
often than you'd think.

Vendor names below are the ones this was built against. Substitute your own; the gotchas are about
the *shape* of the systems, not the brands.

---

## 0. This workspace — the cheapest source, and the one people skip

**Before any external call**, grep the workspace for the email, the user id and the display name:

```bash
grep -ril "<email-localpart>\|<display name>" . --exclude-dir=.git
```

Someone may have already investigated this person. Incident write-ups, support drafts and briefing
files routinely contain a finished root-cause analysis for the user you are about to interview —
including the fix that was applied, whether it worked, and what was promised. It costs one command
and it has returned the entire answer before.

If a workspace file already explains the case, **read it, then verify its key claims against the
live systems rather than repeating them.** Analyses go stale between the write-up and the call, and
a "fixed" recorded on Monday may have been contradicted by the user on Tuesday.

---

## 1. CRM / support inbox — start here when you only have an email

The user id is usually sitting on the contact record, which saves a round-trip.

```
search_crm_objects    objectType=CONTACT  query=<email>
get_crm_objects       objectType=CONTACT  objectIds=[<id>]      # full property set
search_conversations  objectType=CONTACT  objectId=<id>  includeAllDialogue=true
search_crm_objects    objectType=TICKET   filterGroups=[{associatedWith:[{objectType:"contacts", ...}]}]
```

Tool names are from the HubSpot MCP; swap in your own. What matters is that you make **four**
distinct calls — thin search, full record, message thread, tickets — because the first one does not
contain the other three.

**Gotchas**

- A contact *search* typically returns a thin default property set. Always follow with a *get* on
  the record id — that is where the user id, app version, platform, locale and timezone live.
- **The conversation search is usually the only way to read the message thread.** Ticket objects
  carry the original submission but not the replies. Ask for all dialogue explicitly or you miss
  internal notes, which often contain a pre-computed subscription summary.
- Read the **ticket category** critically. Auto-categorisation is frequently wrong — verify against
  the underlying system before repeating it.
- Count the messages. **A thread that ends with our resolution and no user reply means they never
  confirmed.** A thread that ends with *their* message and no reply from us is worse. Flag both.

## 2. Product analytics — the behavioural spine

```
get_user_profile   projectId=<your production project>  userId=<user id>
get_user_timeline  projectId=<your production project>  userId=<user id>  eventLimit=200
```

Discover the project id at runtime rather than hardcoding it — most analytics MCPs expose a
context/list-projects call for exactly this.

**Gotchas**

- **The `userId` is the internal user id, never the email.** An email lookup returns "No user
  found" and it means nothing.
- **Run the profile first, the timeline second.** The profile answers most questions in one call.
- **Do not request full event properties on a 200-event pull** — the response blows the tool's
  token cap and spills to a temp file you then have to parse. Pull the bare timeline, find the two
  or three events that matter, then re-query those with properties.
- **The timeline is capped and truncates silently.** 200 events is roughly a week for an active
  user. Check whether more history exists — if it does, you did not see the beginning of the story,
  and **say so in the Sources section** with the date you can actually see back to.
- Total usage time is the number that matters most and the one nobody looks at. Convert to minutes.
  It is routinely brutal.
- **Lifetime revenue on the analytics profile is unreliable in both directions** — it double-counts
  when purchase events fire both client- and server-side, and it disagrees with the charge amount
  even on clean single-purchase accounts. Never quote it. Go to the payment processor for every
  money number.
- Custom user properties hold the **entire onboarding quiz** — motivation, goal level, study time,
  frequency, topics, age band, how they heard about you. These are the user's own stated words to
  us. Quote them in the dossier and use them in the call. **Their absence is also a finding:** it
  means that onboarding variant never asked, so you genuinely do not know why they are here.
- Also there: experiment variants, feature flags, streaks, current position in the content.
- **Treat any single property as fallible.** Counters like "total lessons completed" routinely
  contradict the position properties on the same profile. If two fields on one profile disagree,
  quote neither and say so.
- The timeline mixes platforms. Watch the device id and platform per row — a user moving web →
  mobile mid-story is a common failure seam.
- Server-side events often carry a null session id and garbage dates. Trust the event time, not the
  display date.
- User properties are stamped **at event time**. A property read today reflects the state at their
  last session, not now — which cuts both ways: it can be stale, or it can be proof of exactly what
  they saw at the moment they complained.

## 3. Payment processor — the billing truth

```bash
grep -E '^\[' ~/.config/stripe/config.toml          # list YOUR configured accounts first
stripe customers list --email <email> --limit 10 --live --project-name <profile>
stripe charges list --customer <cus_id> --limit 10 --live --project-name <profile> > ch.json
stripe subscriptions retrieve <sub_id> --live --project-name <profile> > sub.json
```

**Run the first line before the others, every time.** It is the cheapest way to avoid the most
expensive mistake in this file.

**Gotchas**

- **Query live mode explicitly.** Test mode returns an empty list that looks exactly like "this
  user doesn't exist."
- **Know how many accounts you have, and check all of them.** Funnel purchases, the main app, and
  any secondary brand can each live in a separate account with separate CLI profiles. **An empty
  result on the main account proves nothing.** State which accounts you checked. Getting this
  number wrong is the single most expensive mistake in this file.
- A subscription id prefixed with a funnel name belongs to the funnel account, not the main one.
- **Always redirect CLI output to a file before parsing.** These CLIs write plugin hints into
  stdout, so piping straight into a JSON parser fails with a decode error on the first character.
- **List all customers for the email, not just the first.** One person routinely has several
  customer records — that is often a duplicate-subscription defect. Different invoice prefixes map
  to the different receipt numbers a user quotes in their ticket.
- **Read the price, not just the charge.** A first invoice is often discounted; the recurring
  amount is what they renew at. Someone who paid $39 on a $78 plan renews at $78, and nobody has
  told them.
- **Check the cancel-at-period-end and cancelled-at fields on any user who asked to cancel.** A
  live renewal under an unresolved access failure is a chargeback with a date on it.
- Customer `metadata` is the funnel record: campaign and creative, geo, the user agent (which
  reveals in-app-browser purchases), and the funnel's own internal user id — **which is not your
  app's user id.** A mismatch there is an entitlement bug, visible without touching the database.
- Check failed charges, not just successes. A failed charge followed by a silent retry is a whole
  story on its own.
- Check disputed and refunded on every charge. **Never assume a dispute label on a ticket means a
  chargeback exists** — verify. Refunding an open dispute pays twice; accept instead.

## 4. Web funnel platform — funnel-side subscription and quiz answers

Holds the pre-signup quiz answers and the funnel's own subscription view.

```
<funnel>_get_user_subscriptions  user=<user id>
<funnel>_get_user_properties     user=<user id>
<funnel>_list_user_events        user=<user id>
```

**Gotcha:** funnel API keys expire and rotate. If the call fails, **say so in the Sources section**
rather than quietly omitting it. Payments + analytics together cover most of what it would have
told you.

## 5. Personal email — usually empty, check anyway

```
search_threads  query="<email> in:anywhere"
```

**Gotcha:** support mail usually lives in the support inbox, not a personal mailbox. An empty
result is expected and is not evidence of no contact. Record it as checked.

## 6. Store reviews — only if they left one

Search whatever review data you already pull, by display name. Most users can't be matched; don't
burn time.

---

## One person is not always one account

Identity pinning assumes user id ↔ email is 1:1. **It is not.** A single person routinely holds two
or more accounts, and this is the failure mode most likely to be the entire story:

- A funnel buyer who pays first and signs up second can create a second account at checkout — a
  typo'd address (`ssmith@` vs `smith@`), a different auth provider, or a private-relay address.
  Entitlement anchors to one; they log into the other.
- The support lookup then reads one account and the app reads the other, so **support sees "active,
  paid" while the user sees "free", and both are telling the truth.**
- Manual grants land on whichever account the agent looked up, which is why the same user can be
  "fixed" repeatedly and stay broken.

**Check for it every time, before you build the timeline:**

- Look up the email in the identity system and also search for near-miss variants of it.
- Compare the account creation timestamp to the purchase timestamp. An account created *minutes
  after* a payment is the signature.
- If two ids exist, pull the analytics profile for **both** and compare email, creation time, last
  sign-in, usage minutes, and position in the content. They will disagree, and the disagreement is
  the finding.
- Note that "progress" is measured two ways — total usage and position in the content — and the two
  accounts can each be "further ahead" on a different one. Do not collapse them into a single claim
  about which account the user "really" uses; if the sources disagree, say they disagree.

An entitlement record keyed by subscription id rather than user id can only ever point at one
account, so this class of case **cannot be repaired automatically**. Say so in the dossier: it
changes what can honestly be promised on the call.

---

## Coverage discipline

Name every system you queried in the dossier's Sources section — **including the ones that returned
nothing and the ones that failed**. A prep doc that silently omits a source reads as "we checked
everything" when it didn't.
