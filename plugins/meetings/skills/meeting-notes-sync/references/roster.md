# Resolving People to ClickUp User IDs

Action-item owners arrive as display names. ClickUp mentions need numeric user IDs. Getting this wrong tags the wrong person, silently.

**There is deliberately no roster table in this file.** A hand-maintained member list goes stale the moment someone joins or leaves, and a stale roster fails in the worst way — by confidently resolving to a former employee. Resolve at run time instead, and use this file for the *rules* and the *traps*.

## Resolution order

Apply in order. First confident hit wins. No hit → treat as unmapped.

1. **Previous pages in the same series.** Fetch the last synced page for this series and read its existing mentions. If a name already resolves to one specific `#user_mention#` id across three prior pages of this exact meeting, that is the account the team uses. This is the strongest signal available and it costs one read you are already doing.

2. **Calendar attendee email → ClickUp member email.** Pull the meeting's calendar event, take attendee emails, match against `clickup_get_workspace_members` on `email`. Exact match only.

   ```bash
   gws calendar events list --params '{"calendarId":"primary","timeMin":"<date>T00:00:00Z","timeMax":"<next-day>T00:00:00Z","singleEvents":true,"fields":"items(summary,start,attendees(email,displayName))"}'
   ```

3. **`clickup_resolve_assignees` / `clickup_find_member_by_name`** on the display name — *only* when it returns exactly one match. Two or more matches means stop, not pick.

4. **No confident match** → unmapped. Write the item with the plain name, no mention, and list it in the digest.

Never fall back to fuzzy or nearest-match on names. A near-miss that resolves is worse than a miss that flags.

## Known traps

**One person, two accounts.** At least one contributor in this workspace holds two ClickUp accounts under the same display name — an external/agency address and a company one. The meeting notes for their series consistently use the *external* account, not the company one.

Resolving by display name picks between them arbitrarily. Rule 1 (previous pages) settles it, because the series has been using one of them consistently; rule 2 settles it when the invite went to a specific address. Never rely on rule 3 for a duplicated name — scan `clickup_get_workspace_members` for repeated display names before trusting any name lookup.

**External participants have no ClickUp account.** Agency and partner meetings routinely assign action items to people who aren't workspace members. This is normal, not an error. Plain name, no mention, digest line. Do not create accounts, and do not reassign to the internal person who "owns the relationship".

**Display names differ between systems.** Gemini writes full legal names; ClickUp accounts often use first names or nicknames, and the two may share no substring at all. Rules 1 and 2 route around this by never comparing names to names. Rule 3 exists for the cases they miss and is the weakest link.

**Bot and shared accounts exist** — automation users, admin accounts, shared assistant mailboxes. They match name-ish queries and must never be assigned an action item. Skip them at every rule.

**Some members appear under personal addresses** rather than a company domain — freelancers and contractors. Rule 2 still works: match on whatever address the calendar invite actually used, never on an assumed corporate address.

## Attendees vs owners

The person who owns an action item is not always in `Invited`. Someone can be assigned work in their absence. Resolve owners independently of the attendee list; use attendees only as a *hint* to disambiguate, never as a filter that drops an owner.

## Resolving correctly is not the same as being right

This file solves "which ClickUp account does this name mean". It cannot solve "is this the right person for this task" — that error arrives already baked into Gemini's output.

Worked example from testing:

- Gemini's `Next steps` named two people out of six attendees.
- Rule 2 resolved both correctly — one via a full legal name sharing no substring with their ClickUp display name, matched purely on the calendar invite's email.
- Four attendees were never mentioned at all, despite owning items on the page.
- One correctly-resolved item belonged to a different attendee entirely, confirmed by the organizer.

Perfect resolution, wrong owner. The corroboration gate in `SKILL.md` exists for exactly this: resolution accuracy is necessary, not sufficient. When resolution succeeds but corroboration fails, write the item unassigned.

## Sanity check before writing

Names are written as **plain text**, not `@mentions` — API-written mentions are dead links (see [`clickup-docs.md`](clickup-docs.md#mentions)). So resolution no longer risks pinging the wrong person.

It still matters for correctness. A wrong name against an action item misdirects the work just as effectively as a wrong tag would, only more quietly. Every name written must:

- Belong to a current workspace member (present in `clickup_get_workspace_members` this run).
- Not be a bot or shared account.

A name failing either check becomes `Owner unconfirmed - ` plus a digest line.
