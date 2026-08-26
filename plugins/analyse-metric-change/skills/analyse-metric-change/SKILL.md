---
name: analyse-metric-change
description: >-
  Explain why a product metric moved. Give it a metric (installs, trial starts,
  signups, D1/D7 retention, revenue, conversion) and a timeframe, and it pulls
  Amplitude, shows the trend, and breaks the change down by segment — marketing
  channel, platform, country, language, plan — to say in plain English which
  segments moved the number and what to check. Use when anyone asks "why did X
  go up/down?", "what happened to signups last week?", "which channels drove
  trials?", or wants a metric explained without opening Amplitude themselves.
  Not for: building a permanent dashboard, ad-platform ROAS reporting, or
  store-listing/ASO analysis.
---

# Analyse Metric Change

Turn "why did this number move?" into a decision-ready answer in one shot: the
trend, the segments driving it, and a plain-English readout of what changed.
Self-serve analytics for non-analysts — anyone can run it; only the answer
matters, not knowing where the data lives.

## About

**Privilege level: read-only** — reads Amplitude, writes nothing. Produces an
explanation and a chart link; never modifies data or sends anything.

## Required tools

- An **Amplitude MCP connection** (product analytics). If it isn't connected,
  stop and say so plainly — never guess numbers.
- One config value the runner supplies: the Amplitude **project/app id**. Read
  it from config or ask the user for it on first run. Never hardcode it.

Never print API keys, tokens, or the project id secret. Reference connections by
name.

## Inputs

Accept whatever the user gives; fill gaps with sensible defaults, don't interrogate.

- **Metric** (required): e.g. installs, new signups, trial starts, D1/D7
  retention, subscription conversion, revenue.
- **Timeframe** (default: last 7 days vs the prior 7).
- **Optional focus**: a segment the user already suspects ("just iOS").

## Procedure

1. **Confirm the connection.** Verify Amplitude is reachable. If not, stop and
   report it — no fabricated trends.
2. **Resolve the metric to a real event.** Discover the project's actual events /
   properties before querying (names are project-specific — look them up, don't
   guess). Map the user's plain word to the closest real event; if several fit,
   name them and pick the most likely, noting the choice.
3. **Pull the trend.** Query the metric over the timeframe and the equal prior
   period. Capture current value, prior value, absolute + percent change,
   direction.
4. **Segment the change.** Break the metric down by the segments that explain
   movement — typically marketing channel, platform, country, language, plan,
   new-vs-returning. Rank by **absolute** contribution, not percent (a tiny
   cohort doubling is noise; a big cohort dropping 8% is the story).
5. **Render one chart.** Show the trend visually. Prefer a rendered/linked
   Amplitude chart over a wall of numbers.
6. **Write the readout.** 3–5 lines: what the number did (real figures), the one
   or two segments driving it, the most likely "what changed" stated as a
   hypothesis to verify, and what's noise vs. signal.

## Output shape

```
📊 <metric> — <timeframe>
Headline: <current> vs <prior> (<+/-X, +/-Y%>) — <up/down/flat>
Chart: <rendered or linked>
What moved it:
- <segment A>: <contribution> — main driver
- <segment B>: <contribution>
Read: <2–3 lines, what likely changed + what to verify>
Noise to ignore: <small cohorts that look dramatic but aren't>
```

## Definition of done

**Pass condition (measurable):** the output names the headline change with real
figures (current, prior, absolute + %), ranks at least the top segment driver by
**absolute** contribution, includes a chart link, and states a verifiable
hypothesis — all sourced from a live Amplitude query, zero invented numbers.

**Golden example**
- *Input:* "trial starts, last 7 days vs prior 7"
- *Acceptable output:* "Trial starts 1,240 vs 1,010 (+230, +23%) — up. Main
  driver: paid/iOS, +180 of the +230. Read: the Tuesday iOS creative refresh
  likely drove it — confirm against the ad launch date. Noise: Android +5% on a
  tiny base, ignore." + a chart link.

**Adversarial case (failure handling)**
- *Input:* "why did revenue drop?" while the Amplitude connection is down.
- *Correct behavior:* stop and report "Amplitude isn't reachable — I can't pull
  the trend, and I won't guess." No fabricated figures, no partial numbers
  presented as real.

## Guardrails

- **No connection, no answer.** If Amplitude is unreachable, say so; never invent
  a trend.
- **Absolute over percent** when ranking drivers.
- **Hypothesis, not verdict** — flag likely causes as leads to confirm.
- **One metric per run.** A second question is a second run.
- **Config-driven.** Project id and event names come from config / live lookup,
  never baked into this file.
