# Installing meeting-notes-sync

For a teammate setting this up on their own account.

Each person runs this against **their own** Google Drive and **their own** ClickUp access. There is no central install: Drive doesn't let one account read another's My Drive, and ClickUp visibility differs per person. That's a constraint, not an oversight.

## It only syncs meetings you organized

Read this before rolling it out to the team, because it determines who needs it.

The skill checks each meeting against your calendar and syncs it only if **you** were the organizer. Everything else is skipped. Without that rule, a sprint meeting with eight attendees gets synced eight times into the same ClickUp page.

The practical consequence: **coverage follows organizers, not attendees.** A recurring meeting only gets synced if the person who organizes it has the skill installed. Attending it isn't enough, and an attendee won't even see it flagged — it isn't theirs to report.

So when rolling out, don't start with whoever is most enthusiastic. Start with whoever organizes the recurring meetings that matter. One useful check:

```bash
python .claude/skills/meeting-notes-sync/scripts/scan_sources.py --since 2026-07-01
```

The `Skipped` section names the organizer of each meeting you can see but don't own. Those names are your rollout list.

## What you need first

| Requirement | Check |
|---|---|
| `gws` CLI, authenticated as your work account | `gws drive files list --params '{"pageSize":1}'` returns JSON |
| ClickUp MCP connected | ClickUp tools appear in your session |
| Python 3.9+ | `python --version` |

If ClickUp isn't wired, run `/mcp-setup` and pick ClickUp. Don't hand-edit `.mcp.json`.

**No other skill is required.** The private-topic keyword list ships in `references/private-topics.md`. If your workspace also runs a skill that files Meet recordings into shared drives, it will keep its own copy of a similar list for routing — update both together, because a guard that drifts fails silently in the direction that leaks.

## 1. Dry run first

```bash
python .claude/skills/meeting-notes-sync/scripts/scan_sources.py --since 2026-08-01
```

You should see your recent meetings grouped by title and time, with their Drive location. If you see zero folders scanned, `gws` isn't authenticated. If you see meetings you don't recognise, you have access to Shared Drives whose meetings aren't yours — that's fine, the organizer filter and the registry both gate what actually gets written.

## 2. Build your registry from your own calendar

**This is the step people skip, and it's the one that matters.** It is also mostly automated.

```bash
python .claude/skills/meeting-notes-sync/scripts/audit_calendar.py --days 120
```

The script inventories every **recurring meeting you organize**, works out its cadence, and lists which Drive artifacts exist for it. It deliberately excludes 1:1s (two attendees or fewer), personal holds (no attendees), and one-offs — reporting those as counts only, never by title, so private meeting names stay out of an install report.

Then hand the output to the skill and ask it to build the registry. For each series it will:

1. Search ClickUp for candidate destination docs and pages.
2. Compare the candidate page dates against the artifact dates the script found.
3. Mark the row ✅ **verified** when three or more occurrences align, and draft it into `state/registry.md` (personal, gitignored — the shipped registry file is a rows-free template).
4. Ask you **only** about what it cannot reconcile.

### What it will come back to you about

| Case | What you decide |
|---|---|
| **Two candidate docs** for one series | Which is canonical. Writing to the wrong one splits that meeting's history permanently. |
| **No ClickUp home found** | Whether one should exist, or whether this meeting genuinely has no notes page. |
| **Dates don't line up** | Usually means the candidate doc belongs to a *different* meeting with a similar name. |
| **Only one or two occurrences** | Not enough evidence yet. Monthly series need a few months. |

Everything it reconciles cleanly needs no input from you at all.

### Status meanings

Only ✅ **verified** rows write unattended. ⚠️ provisional and ⛔ blocked rows report instead, which is a safe place to sit indefinitely.

Expect **few rows**. Only meetings you personally organize need one, and 1:1s and personal holds are excluded — so a registry with a handful of rows is normal, not a sign the audit missed something.

This sweep is worth trusting: run by hand across nine rows, it caught **four wrong ones** — two pointing at the wrong destination, one whose trigger matched entirely different meetings, and one wrong about both its trigger and its page structure. A skill writing to the wrong ClickUp page unattended is worse than a skill that reports and waits.

## 3. Schedule it

Default is **10:00 local, daily**:

```
Run the meeting-notes-sync skill. Sync any new meetings to their ClickUp pages,
then send me the digest as a Slack DM.
```

Adjust the time to suit, but keep these constraints:

- **After** any task that moves recordings into shared drives, so artifacts have settled before the scan.
- **Not 09:30** — the follow-up runner owns that slot.
- **Not immediately post-meeting.** Gemini notes land minutes to hours after a meeting ends.

Twice daily (10:00 and 16:00) is reasonable if you want faster turnaround. The run is idempotent and cheap, so frequency costs little — see the trigger discussion in [`SKILL.md`](SKILL.md#the-daily-run).

## 4. Watch the first week

Read the digest daily for the first week. You're checking two things:

- **`no-clickup-page` entries that surprise you.** Either the meeting genuinely has no page (fine, that's the flag working), or your registry row points at the wrong doc.
- **Anything under `Privacy refusals`.** That means a sensitive-sounding meeting has a notes page in a team-wide space. Worth knowing regardless of this skill.

## Configuration that's yours, not shared

| File | Shared or personal |
|---|---|
| `SKILL.md`, `references/*`, `scripts/*` | **Shared** — identical for everyone, update centrally |
| `state/registry.md` | **Personal** — your meetings, your teams' doc layout. Built by the install audit. |
| `state/processed.json` | **Personal** — never commit, never share |

`state/` is gitignored in full. If you wipe it you lose your registry and have to re-run the audit, but nothing is corrupted: the marker-block check in ClickUp still prevents double-writes.

## Sharing it onward

Use `/export-skill meeting-notes-sync` to package it. Note for whoever receives it:

- Nothing org-specific ships. The registry file is a rows-free template and the method files name no meetings or people, so the package is identical for every recipient. Each person builds their own rows with the install audit.
- The private-topic keyword list ships with the skill in `references/private-topics.md`, so there is nothing else to install.

## If something breaks

Errors surface verbatim in the digest rather than being retried away. The common ones:

| Digest says | Means |
|---|---|
| `found no folders to scan` | `gws` auth expired. Re-authenticate. |
| `403` on a write | You have read-only access to that space. A human grants access; the skill won't route around it. |
| `404` on doc or page | The page was deleted or moved out of your access. Re-check the registry row. |
| Same `unmatched-series` every week | A real recurring meeting with no registry row. Add one. |

Don't fix a failing row by pointing it at a different doc that happens to work. That's how notes end up in the wrong team's space.
