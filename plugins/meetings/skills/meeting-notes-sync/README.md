# Meeting Notes Sync

Keeps ClickUp meeting notes up to date from the meetings **you organize** — and tells you which of them never got written up at all.

## What it does

After a meeting, Google Meet's "Notes by Gemini" lands in Drive. This skill finds new ones daily, matches each meeting to its ClickUp meeting-notes page, and appends the decisions and any action items that aren't already recorded there, each with its owner's name.

Meetings with notes in Drive but **no** ClickUp page get flagged in a private digest. Not every meeting needs a page; you just get told which ones don't have one.

**It does not notify anyone.** ClickUp's API cannot create a working @mention in a doc — every syntax produces a dead link that looks like a tag but pings nobody. Owners are written as plain names, and the daily Slack digest lists who owns what. That digest is the handoff.

## It only syncs meetings you organized

This is the first thing to understand, because it decides who on the team needs it.

The skill checks each meeting against your calendar and syncs it only if **you** were the organizer. Everything else is skipped. Without that, a sprint meeting with eight attendees would get synced eight times into the same page by eight different people.

**Coverage therefore follows organizers, not attendees.** A recurring meeting gets synced only if the person who *organizes* it has this installed. Attending isn't enough — and an attendee won't even see it flagged, because it isn't theirs to report.

So roll it out to the people who own recurring meetings, not just whoever is keen. Run the scanner once and read the `Skipped` section — it names the organizer of every meeting you can see but don't own. That's your rollout list.

## What it deliberately will not do

These guardrails are why it's safe to run unattended:

- **Never creates a ClickUp page.** It only appends to pages a human already made. Whoever created the page also chose who can see it — the skill inherits that decision instead of guessing at access.
- **Never overwrites your notes.** It appends one clearly-marked block at the end of the page, using ClickUp's server-side append so your existing content is never re-parsed or altered.
- **Refuses to guess.** Zero matching pages, or two, means it flags and stops rather than writing to the wrong place. Same for an ambiguous calendar match.
- **Refuses to write a sensitive meeting into a team-wide space.** 1:1s, comp, hiring, and finance meetings are checked; if their page sits somewhere broad, it flags instead of writing.

## Requirements

| Requirement | Notes |
|---|---|
| `gws` CLI, authenticated | Google Drive/Docs/**Calendar** access as your work account. Calendar is not optional — it's how the organizer check works. |
| ClickUp MCP connected | Run `/mcp-setup` and pick ClickUp if it isn't wired |
| Python 3.9+ | For the Drive scanner |

No API keys are stored by this skill. It uses your existing authenticated `gws` and ClickUp connections.

## Install

1. Download this file.
2. In Claude, run: `/import-skill <path-to-this-file>`
4. **Read `INSTALL.md` before enabling the scheduled run.** There's a registry-verification step that genuinely matters — every meeting-series row ships as `provisional` and won't write unattended until a human confirms it points at the right ClickUp doc.

## Before you trust it

Run it manually for a week and read the digest. You're looking for `no-clickup-page` entries that surprise you — those mean either the meeting really has no page, or your registry row points at the wrong doc. Twenty minutes of verification up front beats notes landing in the wrong team's space.

## Adapting it beyond Ling

The matching *method* transfers anywhere. The `references/meeting-registry.md` rows do not — they hold Ling-specific ClickUp doc IDs and need rebuilding from scratch for another workspace.
