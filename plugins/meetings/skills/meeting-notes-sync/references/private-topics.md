# Private-Topic Guard

The keyword list that decides whether a meeting is sensitive enough that its notes must not be written into a team-wide space.

Self-contained on purpose, so this skill has no install-time dependency on any other skill.

## The list

A case-insensitive match on any of these in the **meeting title** marks the meeting as private-topic:

```
financial, finance, forecast, p&l, budget, payroll, salary, compensation,
comp review, bonus, equity, headcount, hiring, recruitment, candidate,
performance review, 1:1, one-on-one, 1-on-1, coffee break, offboarding,
termination, board, investor, legal, contract review, leadership, exec,
visa, work permit
```

**Exception:** `user interview` and `user research` are product meetings, not hiring. If either appears in the title, the guard does **not** fire on `candidate` or `interview`.

## What a hit means

A hit does **not** mean skip. It means: this meeting may only be written to a page in a **private** space.

| Situation | Action |
|---|---|
| Guard hit, matched page is in a private space | Proceed normally |
| Guard hit, matched page is in a team-wide space | **Refuse the write**, flag it in the digest |
| No guard hit | Proceed normally |

Refusing is cheap: it produces one digest line, and a human either moves the page or waves it through. Guessing wrong publishes a compensation conversation to everyone.

## Why it is deliberately over-broad

A false positive costs one manual review. A false negative puts salary data somewhere the whole company can read it. The list is tuned for the second failure, not the first.

Do not narrow it to reduce digest noise. If a specific recurring meeting is being flagged unnecessarily, the fix is confirming its page lives in a private space, not removing the keyword.

## Keeping it current

Add a keyword whenever a sensitive meeting type appears that the list would have missed. Removing one needs more thought than adding one.

If your workspace also runs a skill that files Meet recordings into shared drives, it will have its own copy of this list for routing. The two should be updated together — a guard that drifts between two places fails silently, and in the direction that leaks.
