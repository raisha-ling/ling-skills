---
name: stress-test-plan
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

# Stress Test Plan

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

## About

- **Privilege level:** read-only — it asks questions and reads the local environment (filesystem, tools) to find facts; it writes nothing and sends nothing.
- **Tools needed:** none required. If the plan under discussion involves a codebase, having repo access lets it dispatch sub-agents to check facts instead of asking the user for them.
- **Where it runs:** any conversation where the user wants a plan, decision, or idea stress-tested before acting on it.

## The Process

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

## Definition of done

**Pass condition.** Every round asked is the true current frontier — no question is asked before its prerequisite is settled, and no settled decision goes back to the user for confirmation. Any fact the environment could answer (a file's contents, whether a dependency exists, current config) is found by a sub-agent, never asked of the user. The session only ends once a round comes up empty and the user has explicitly confirmed shared understanding — the skill never starts acting on the plan itself.

**Golden example.** User: "grill me on this plan: add a retry queue for failed webhook deliveries." Round 1 asks the frontier-level questions only — e.g. "Q1: what counts as a failure worth retrying (5xx only, or timeouts too)?" and "Q2: is there already a queue/job system in this repo, or does one need to be picked?" — each with a numbered recommendation, and dispatches a sub-agent in parallel to check the repo for an existing queue library so Q2's answer can be confirmed or corrected without asking the user to go look. Later rounds (e.g. retry backoff policy, max attempts, dead-letter handling) wait until the failure-criteria and queue-choice decisions are settled, since they depend on those answers.

**Adversarial case.** User answers a question in a way that invalidates an assumption baked into an earlier "settled" branch (e.g. round 2 reveals the queue needs to be cross-region, contradicting a round-1 recommendation that assumed a single-region job runner). The skill must reopen the affected branch and re-ask the downstream questions with corrected recommendations, rather than silently carrying the stale assumption forward or asking the user to notice the conflict themselves.
