# Reading Gemini Notes

Google Meet's "Notes by Gemini" docs are the primary input. They are already structured, which is most of why this skill is cheap.

## Naming

Meet names artifacts:

```
<Title> - <YYYY/MM/DD HH:MM TZ> - <Kind>
```

`<Kind>` is `Notes by Gemini`, `Recording`, `Recording 2`, or `Transcript`. Everything sharing the base string is one meeting.

## Renamed files

A renamed artifact loses the timestamp the matcher needs. The scanner recovers these automatically — no prompting — when it can be confident, and drops them when it can't.

### Do not read the date out of the document

**Gemini notes contain no meeting date.** Verified against the corpus: the body has a title, `Invited`, `Attachments`, then the content sections. Nothing dates the meeting.

What the body *does* contain is incidental dates inside the discussion — "the budget was scaled on the 12th", "the campaign launched in April". A "find a date in the document" heuristic latches onto the first of those and returns a real date, matching a real ClickUp page, for a **different** meeting. It then writes into it unattended.

This is the trap the rest of the skill is built to avoid, so it's worth stating twice: dates in the text describe the subject matter, not the meeting.

### What is used instead

| Signal | Why it holds |
|---|---|
| Drive `createdTime` | Survives renaming. Gemini writes the doc within hours of the meeting ending. |
| A matching calendar event | Confirms the date *and* supplies the organizer check in one step. |

### The confidence gate

Recovery runs automatically and only proceeds when **all** hold:

1. The file is a Google Doc.
2. It is genuinely a Gemini artifact — identified by content, not name: either Gemini's own review disclaimer, or at least three of its canonical headings (`Invited`, `Summary`, `Decisions`, `Next steps`, `Details`).
3. Exactly one calendar event started between 30 minutes after and 6 hours before `createdTime`, and its title matches — or there is exactly one event in that window regardless of title.
4. You organized that event.

Anything else is dropped with a reason, never guessed at and never raised as a question.

### Step 2 is the one that matters

Most unmatched files in a meetings folder are **not renamed artifacts at all** — they're human documents that happen to live there. Every unmatched file found during testing fell into one of two shapes, and all were correctly rejected:

| Shape | Why it must not sync |
|---|---|
| **Empty note template** — `Attendees:` / `Notes` / `Action items`, nothing filled in, often created *before* the meeting | The meeting usually already has its own correctly-named Gemini doc, so syncing the template duplicates it, with no content. |
| **Interview or agenda script** — a list of questions to ask, placeholders like `Recording: XXXX` left unfilled | Prep material, not a record of anything that happened. |

Syncing either would push an empty template or a question list into ClickUp as if it were meeting notes. The content check is what stops that, and it's why recovery keys on document *structure* rather than on filename patterns.

The timestamp in the **filename** is the meeting time and is the date to match against ClickUp `date_created`. Don't use the Drive file's `createdTime` for matching — Gemini writes the doc some time after the meeting ends, and for a late-evening meeting that can land on the next calendar day.

## Document structure

Read with `gws docs documents get` and walk `body.content`. Headings (`namedStyleType` containing `HEADING`) delimit sections:

| Section | Contents | Use |
|---|---|---|
| *(title)* | Meeting name | Confirm the series match |
| `Invited` | Attendee list | Resolving owners to ClickUp IDs |
| `Attachments` | Linked files | Ignore |
| `Summary` | One dense paragraph, headings run together without spacing | Optional — usually too unstructured to be worth pasting |
| `Decisions` | Bulleted, `<Decision title> <explanation>` | **Write these.** |
| `Next steps` | `[Person Name] <Task>: <detail>` | **These are the action items.** Owner is pre-attributed. |
| `Details` | Long narrative bullets, one per topic | Skip by default — this is where the token cost is |

### `Next steps` is the win

Gemini already extracted action items *with owners*:

```
[Full Name] Update Reports: Integrate the spreadsheet data into the weekly project report.
[Other Name] Share Tracking Sheet: Distribute the current tracking sheet to the team.
```

Parse as `^\[(?P<owner>[^\]]+)\]\s*(?P<task>.+)$`. The task text is written as-is — do not rewrite or "improve" it, it is the record of what was said, and paraphrasing invents commitments.

An empty or missing `Next steps` section is normal and fine. Write the decisions, note zero action items, move on.

### The owner in brackets is a suggestion, not a fact

Treat `[Person Name]` as a hint requiring corroboration. Measured against a real meeting during testing, with that meeting's own organizer confirming the corrections:

| Problem | Evidence |
|---|---|
| **It names a fraction of the room.** | Six calendar attendees; `Next steps` named **two**. Four people who owned work on that meeting's page appeared in no attribution at all. |
| **It credits the speaker, not the owner.** | One item was attributed to the person who happened to be discussing it. The organizer confirmed it belonged to a different attendee entirely. |
| **It contradicts the human record.** | Two further items named owners the page assigned to someone else. In one case Gemini's own `Details` says only "a participant volunteered" — the page identifies who. |

Four of thirteen owners wrong on a single meeting. That is not an edge case to handle later.

Consequences for this skill:

- Tag an owner only under the corroboration rules in the `Decide whether you can name an owner` step of `SKILL.md`. Otherwise write the item unassigned.
- **Where Gemini disagrees with the page, the page wins.** A person wrote it with context the model lacked.
- Never treat the absence of a name in `Next steps` as evidence someone has no action items. It usually means Gemini didn't attribute them.

The same caution applies to `Details`, which can refer to one person two ways inside a single document — a full legal name in one sentence, a nickname in the next, both describing the same account.

## Boilerplate to strip

Gemini injects feedback prompts into the body. These are not content and must never reach ClickUp:

- `We've updated the Decisions section using your feedback.`
- `Let us know what you think: Helpful or Not Helpful`
- `Did the screenshots in this section make your notes better or worse?`
- `You should review Gemini's notes to make sure they're accurate. Get tips and learn how Gemini takes notes`
- `How is the quality of these specific notes? Take a short survey…`
- A bare `Aligned` line under `Decisions`

Match these as prefixes rather than exact strings — the wording shifts between Gemini versions. When something looks like product chrome rather than meeting content, drop it.

## Accuracy caveat

Gemini's own disclaimer is there for a reason: these notes are a model's summary, not a record. Two consequences for this skill:

- **Attribute the source.** Every appended block ends with a link back to the Gemini doc so a reader can check. That link is not decoration — it is also the idempotency marker.
- **Never assert beyond the notes.** Don't infer due dates that aren't written down, don't merge two similar action items, don't resolve a decision the notes describe as open.

## Transcripts

If a `- Transcript` artifact exists alongside the notes, it is a Google Doc of the raw dialogue. **Do not read it by default.** It is long, it costs real tokens, and Gemini has already extracted what the skill writes.

Fetch it only when explicitly asked, or when a specific action item's owner is ambiguous and the transcript would settle it. Even then, read the relevant span, not the whole document.

As of the 2026-08-20 audit, Ling has transcription disabled workspace-wide, so this section is mostly forward-looking.
