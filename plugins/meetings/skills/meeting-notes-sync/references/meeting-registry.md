# Meeting Registry — Format and Method

How the skill decides which ClickUp page a meeting belongs to.

**This file ships with no rows in it, and should stay that way.** The actual rows are personal: they describe the meetings *you* organize and where *your* teams keep notes. They live in `state/registry.md`, which is gitignored and never shared, alongside `state/processed.json`.

Build yours with the install audit rather than by hand — see [Building your registry](#building-your-registry).

## Why matching works this way

Two independent problems, solved separately.

**Which series?** Titles are stable and human-authored, so a lookup table handles them. What it cannot handle is a title that is new, or one closely resembling a *different* meeting. Two similarly-named meetings are often entirely separate series with different attendees and cadences. Verify against dates before trusting a name.

**Which page within the series?** Page titles are unreliable. In practice they use many date formats, drift *within* a single document, and sometimes name the period being discussed rather than the meeting date — a monthly review held in July may sit on a page titled for June. Some carry no date at all.

**The ClickUp API returns `date_created` per page.** That timestamp is unambiguous and needs no parsing. Match on it; use the title only to confirm.

## Matching method

1. Title → series row. Case-insensitive. First hit wins; order matters where patterns overlap.
2. Within that row's `Doc` + `Parent page`, list pages and keep those whose `date_created` falls between **10 days before** and **3 days after** the meeting.
3. Exactly one candidate → write. Zero → `no-clickup-page`. Two or more → `ambiguous`.
4. For `rolling` series, skip step 2 — the target page is fixed.
5. For `dated (quarter parent)` series, resolve the current quarter's parent page first, then run step 2 inside it.

### Why the window is asymmetric

Pages get created **early**, not late. Teams that run an agenda prepare the page days ahead, fill in the agenda, then hold the meeting against it. Observed series create their pages around five days in advance; a symmetric ±3 window missed them entirely and reported `no-clickup-page` — the worst available failure, because it reads as "nobody wrote this up" when the page existed and was already detailed.

10 days back covers agenda-first prep without reaching the previous occurrence of a weekly series. Writing up more than 3 days after the fact is rare, so the forward edge stays tight. Two candidates inside one window is a flag, not a coin toss.

## Row format

Keep rows in `state/registry.md` as a table with these columns:

| Column | Notes |
|---|---|
| **Meeting title contains** | Lowercase substring match. Key it on the **series name** with any per-occurrence month or date stripped — a trigger containing "August" matches exactly once. `audit_calendar.py` outputs the collapsed `series_name` for this. |
| **ClickUp space** | Name + numeric id. Also records whether the space is private. |
| **Doc** | Name + doc id. |
| **Parent page** | Name + page id, or *(root)*. Take this from the page's own `parent_page_id`, not from a search result's displayed hierarchy — they can disagree. |
| **Kind** | `dated`, `dated (quarter parent)`, or `rolling`. |
| **Status** | ✅ verified · ⚠️ provisional · ⛔ blocked. |

Add a short note under any row that is not plainly verified, saying what is unresolved and who can settle it.

### Status meanings

| Status | Behaviour |
|---|---|
| ✅ **verified** | Writes unattended. Three or more occurrences aligned, and someone who attends confirmed the destination. |
| ⚠️ **provisional** | Reports only. Destination plausible but under-evidenced — often a monthly series with too few occurrences, or one with no recordings to check against. |
| ⛔ **blocked** | Reports only. Something is actively wrong or undecided: two candidate docs, or a trigger matching the wrong meetings. |

Provisional and blocked are safe places to sit indefinitely. A row that reports costs a digest line; a row that writes to the wrong page corrupts a meeting's history.

## Building your registry

```bash
python .claude/skills/meeting-notes-sync/scripts/audit_calendar.py --days 120
```

The script inventories every recurring series **you organize**, with its cadence and the Drive artifacts found for each. It excludes 1:1s, personal holds, and one-offs, reporting them as counts without titles.

Hand the output to the skill. For each series it searches ClickUp for candidate docs, compares their page dates against the artifact dates, drafts the rows, and asks you only about what it cannot reconcile.

Only series you organize need rows. A meeting you merely attend is somebody else's to sync, so it will never reach the matching step on your machine — the organizer filter drops it first.

## What does not get a row

- **Series with no Drive artifacts.** Nothing will ever sync for them regardless of what the registry says, and a row that never fires later reads as coverage.
- **1:1s and personal holds.** Excluded by the audit on attendee count, and they should not appear in a shared notes registry at all.
- **Meetings you don't organize.** Someone else's to sync.
- **Anything speculative.** Add a row when the digest reports the same `unmatched-series` repeatedly — that is evidence the meeting is both real and recurring.

## Verifying a row

1. List the parent page's children and read their `date_created`.
2. List the Drive artifacts for that series and read their dates.
3. Compare the sequences. Three or more aligned occurrences → verified. One occurrence, or a mismatch → leave provisional and write down why.
4. Confirm with someone who attends that the doc is genuinely where the team keeps these notes.

This sweep is worth running rather than trusting inference. Run once across nine hand-written rows, it found **four wrong** — two pointing at the wrong destination, one whose trigger matched entirely different meetings, and one wrong about both its trigger and its page structure.

Record the verification date in the row.

## Space privacy

Some destinations sit in private spaces. The skill reads space privacy from ClickUp at run time rather than trusting the registry — see [`clickup-docs.md`](clickup-docs.md#checking-space-privacy). A row records the *destination*, never the *permission*.

## Related

- Private-topic keyword list → [`private-topics.md`](private-topics.md).
- Page write mechanics → [`clickup-docs.md`](clickup-docs.md).
- Name → user ID resolution → [`roster.md`](roster.md).
