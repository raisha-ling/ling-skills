# ClickUp Docs — Write Mechanics

> ## Verified behaviour — tested live 2026-08-21
>
> Everything below was established by writing to a real page and reading it back, not inferred. Earlier versions of this file asserted several of these wrongly.
>
> | Technique | Verdict |
> |---|---|
> | `content_edit_mode: "append"` | ✅ **Use this.** Merges server-side; the existing page is never re-parsed and never altered. |
> | `content_edit_mode: "replace"` | ⛔ **Never.** Round-trips the whole page through ClickUp's markdown importer, destroying bookmark/embed widgets, un-nesting attachments, flattening checkbox state, and rewriting content it never received. Not recoverable through the API. |
> | `[@Name](#user_mention#<id>)` | ⛔ **Never.** Produces a **dead link** — renders with the right name, looks like a tag, but clicking does nothing and nobody is notified. Worse than a plain name, because readers assume the person was told. |
> | `- [ ]` checkboxes | ✅ Works in appended content. |
> | `<!-- html comments -->` | ⛔ **Never.** They render as visible literal text **and** poison the line they sit on, causing the rest of that line — including any mention — to render as raw markdown. |
>
> ### Neither the read-back nor the render proves a mention works
>
> `[@Name](#user_mention#<id>)` reads back as `http://#user_mention#<id>`. That prefix turns it into a hyperlink to a nonexistent URL. It still **renders with the correct name**, so the page looks right — but the link is dead and no notification is sent.
>
> This was misdiagnosed twice in a row, in opposite directions: first blamed on the mention syntax when an HTML comment was poisoning the line, then declared working because it *looked* correct on the page. **Rendering correctly is not evidence a mention functions.** The only proof is the person confirming they were notified.
>
> ### Idempotency without hidden markers
>
> Since comments are unusable, the visible provenance line is the marker. The `Source:` link carries the Gemini doc URL, which is unique per meeting — searching the page for that URL answers "already synced?". It is meaningful to a reader, which a hidden comment never was.
>
> Trade-off: a Drive file id differs between each person's copy of the same meeting's notes, so this is a weaker cross-person guard than a calendar event id would be. The organizer filter is what actually prevents two people syncing the same meeting; this is the backstop.
>
> ### Because append cannot be undone
>
> There is no API delete for appended content — removing it needs `replace`, which is banned above. **A bad append is cleaned up by a human in the ClickUp UI.** Get the block right the first time, and keep it a single contiguous, obviously-deletable chunk.


## Page IDs and hierarchy

A ClickUp doc URL is `app.clickup.com/{workspace}/docs/{doc_id}/{page_id}`. Pages nest arbitrarily deep.

```
clickup_list_document_pages(document_id, max_page_depth=-1)
```

Returns the full tree — `id`, `name`, `parent_page_id`, nested `pages[]`. Names only, no content, so it's cheap. Use it to walk to the registry's parent page and enumerate its children.

```
clickup_get_document_pages(document_id, page_ids=[...], content_format="text/md")
```

Returns content **plus** the fields that matter for matching:

| Field | Use |
|---|---|
| `date_created` | **The match key.** Epoch ms. Unambiguous, unlike page titles. |
| `date_updated` | Detect edits since last sync. |
| `content` | Read before writing. Search it for the Gemini doc URL to see whether this meeting is already synced. |
| `creator_id`, `authors`, `contributors` | Who has touched the page. Useful for resolving the right account for a repeated participant. |

`content_format="text/md"` is required. The default (`text/plain`) strips the mention syntax you need to preserve.

## Mentions

ClickUp doc mentions are plain markdown links with a magic href:

```
[@Full Name](#user_mention#12345678)
```

**Do not write mentions through the API. Use plain names.**

The form above is what ClickUp stores for mentions *it* created, which is why existing pages are full of it. Written back through the API, ClickUp prefixes the href with `http://`, producing a hyperlink to a nonexistent URL. The result renders with the correct name and looks exactly like a tag — but clicking does nothing and the person is never notified.

Three syntaxes were tried live on 2026-08-21 (`[@Name](#user_mention#id)`, `@[Name](id)`, bare `@Name`). None produced a functioning mention.

A dead link that looks like a tag is **worse than a plain name**: a reader assumes the person was notified and has seen the item. Write `Full Name - <task>` instead, and treat the digest as the actual handoff.

If notifying people is a hard requirement, the route with a typed assignee field is a ClickUp **task**, not a doc mention. That is a different shape of skill and needs its own verification.

Resolution still matters for getting the name right — see [`roster.md`](roster.md).

## Where new content goes

**One appended block at the end of the page.** Not merged into the page's existing sections.

That is a deliberate retreat from an earlier design. In-section merging reads better, but it requires `replace`, and `replace` destroys widgets, attachments and checkbox state on any page that has them. Append is the only write mode that cannot damage a page, so it wins.

### Block shape

```markdown

---

**Synced from Gemini meeting notes**

**Decisions**

- <decision>

**Action items not already captured above**

- [ ] <Full Name> - <task>
- [ ] Owner unconfirmed - <task>

Source: [Notes by Gemini](<drive_url>)
```

Rules:

- **Start with a leading blank line and a `---` rule.** The block must read as clearly separate from what a human wrote, and be one contiguous chunk somebody can select and delete.
- **Plain names only.** No `@mention` markup — it renders as a convincing dead link that notifies nobody.
- **Checkboxes survive**, so use them for action items to match how the rest of the page reads.
- **Unresolvable owner → `Owner unconfirmed - `** rather than a guessed mention.
- **`Source:` is the idempotency marker.** Search the page for the Gemini doc URL before writing; present means already synced.
- **One block per meeting.** If a page somehow needs two, that means two meetings matched one page — flag `ambiguous` instead.

### Idempotency: the visible Source link

There is no hidden marker, because HTML comments are unusable (see the table at the top). The `Source:` line carrying the Gemini doc URL is the marker.

Before writing, search the page content for that URL. Present → already synced, stop.

The trade-off worth knowing: each person gets their own Drive copy of a meeting's notes, with a different file id, so two people syncing the same meeting would not see each other's marker. The **organizer filter** is what actually prevents that — only one person owns a meeting. This marker is the backstop for re-runs by the same person, and it survives losing the state file.

### Reverting a run

**In the ClickUp UI, by hand.** Select the block from its `---` rule to the `Source:` line and delete it.

There is no API route: removing appended content would need `replace`, which is banned. That is the cost of append-only, and it is why the block must be one contiguous chunk that is obvious to select. Do not scatter synced content around the page.

## Writing

```
clickup_update_document_page(
    document_id, page_id,
    content=<the block>,
    content_edit_mode="append",
    content_format="text/md",
)
```

Sequence:

1. `clickup_get_document_pages(..., content_format="text/md")` — read the page.
2. Search for the Gemini doc URL. Present → stop, already synced.
3. Subtract anything the page already covers (see the `Subtract what the page already says` step in `SKILL.md`). Nothing left → write nothing at all.
4. Append the block. Start the content with a blank line so it does not run onto the last existing line.
5. Re-read and confirm the block is present.

Step 5 is not optional — record the meeting as processed only after it passes. Expect mention hrefs to read back with an `http://` prefix; that is a serialization artifact, not a failure.

Note there is no diff assertion here, and none is needed: `append` never rewrites existing content, so there is nothing to protect. That check only existed to make `replace` survivable, and it could not do even that — it validated the computed string, not what ClickUp did on save.

`clickup_merge_document_page` exists and looks relevant. Avoid it: its merge semantics are undocumented, and `append` already does the job safely.

## Checking space privacy

The private-topic guard needs to know whether a destination is team-wide or restricted.

```
clickup_get_workspace_hierarchy(max_depth=0)
```

lists spaces the **authenticated user** can see. That is the key subtlety: it reflects *your* access, not the space's sharing settings. A space you can see may still be private to a small group, and a space that is genuinely team-wide looks identical.

So treat it as a signal, not proof, and resolve the guard conservatively:

- Destination space is one the registry marks as private (leadership, HR, or a personal space) → treat as private.
- Destination space is anything else → treat as **team-wide**, and refuse the write when the private-topic guard fired.

Refusing is cheap — it produces a digest line and a human moves the page or waves it through. Guessing wrong publishes a comp conversation.

## Failure modes

| Symptom | Cause | Response |
|---|---|---|
| `404` on doc or page | Page deleted, or outside your access | Flag with the ID. Don't retry, don't search for a replacement. |
| Write succeeds, re-read shows no block | Content silently truncated (very long pages) | Report verbatim. Do not mark processed. |
| Mentions render as literal text | Wrong href shape, or a user ID that isn't a workspace member | Check against [`roster.md`](roster.md). An external person has no ID — write the plain name. |
| `403` on write | Read-only access to that space | Flag. This is a permissions question for a human, not a retry. |

Stop on the first failure. Two attempts maximum. Never fall back to a different destination.
