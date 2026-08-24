#!/usr/bin/env python3
"""Inventory the recurring meetings you organize, and what Drive holds for them.

Read-only. Run once at install time to build the registry, and again whenever
coverage looks wrong.

This is half of the audit. It does the deterministic part -- which recurring
series you own, how often they meet, and which Drive artifacts exist for each.
The ClickUp half (finding the destination doc and checking date alignment) is
done by the skill, because scripts cannot reach the ClickUp MCP.

Only series you ORGANIZE are inventoried, matching the skill's sync rule: a
meeting you merely attend is somebody else's to sync, so it needs no row in
your registry.

Usage:
    python audit_calendar.py                 # last 120 days
    python audit_calendar.py --days 180
    python audit_calendar.py --min-occurrences 2
    python audit_calendar.py --json          # for the skill to consume
"""

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan_sources import (  # noqa: E402
    gws, find_folders, list_children, parse_artifact,
    normalize_title, titles_match,
)


def fetch_instances(days):
    """Every calendar instance in the window, with its recurring-series id."""
    now = datetime.now(timezone.utc)
    params = {
        "calendarId": "primary",
        "timeMin": (now - timedelta(days=days)).isoformat().replace("+00:00", "Z"),
        "timeMax": (now + timedelta(days=1)).isoformat().replace("+00:00", "Z"),
        "singleEvents": True,
        "orderBy": "startTime",
        "fields": "nextPageToken, items(id,recurringEventId,summary,"
                  "start(dateTime),organizer(email,self),attendees(email))",
        "maxResults": 250,
    }
    items, cursor = [], None
    while True:
        if cursor:
            params["pageToken"] = cursor
        page = gws(["calendar", "events", "list"], params)
        items.extend(page.get("items", []))
        cursor = page.get("nextPageToken")
        if not cursor:
            break
    return items


MONTHS = ("january february march april may june july august september "
          "october november december jan feb mar apr jun jul aug sep sept "
          "oct nov dec").split()

# Trailing words that are part of the occurrence label, not the series name.
OCCURRENCE_WORDS = {"check", "in", "checkin", "session", "part", "week",
                    "meeting", "update", "sync", "review", "q1", "q2", "q3", "q4"}


def series_key(title):
    """Collapse per-occurrence titles onto one series.

    Many recurring meetings put the month or a date in the title -- "<Name> -
    August Check In", "<Name> - July Check In". Grouped verbatim, every
    occurrence looks like its own one-off series and nothing is ever detected
    as recurring. Strip the trailing segment when it is clearly an occurrence
    label rather than part of the name.
    """
    norm = normalize_title(title)
    parts = [p.strip() for p in title.split(" - ") if p.strip()]
    if len(parts) > 1:
        tail = normalize_title(parts[-1])
        words = set(tail.split())
        looks_datey = (
            any(m in words for m in MONTHS)
            or any(t.isdigit() for t in words)
            or (words and words <= OCCURRENCE_WORDS)
        )
        if looks_datey:
            return normalize_title(" - ".join(parts[:-1]))
    return norm


def cadence_of(dates):
    """Describe the gap between occurrences in plain words."""
    if len(dates) < 2:
        return "unknown (one occurrence)"
    gaps = [(b - a).days for a, b in zip(dates, dates[1:])]
    med = statistics.median(gaps)
    for limit, label in ((2, "daily-ish"), (8, "weekly"), (11, "~10-daily"),
                         (17, "biweekly"), (24, "~3-weekly"), (45, "monthly"),
                         (100, "quarterly")):
        if med <= limit:
            return f"{label} (median {med:.0f}d)"
    return f"irregular (median {med:.0f}d)"


def collect_artifacts():
    """Every Meet artifact visible to this account, grouped by series.

    Keyed on `series_key`, not the raw title. Meet names each artifact after
    that occurrence's calendar title, so a series carrying a month in its name
    produces a differently-named artifact every time. Grouping verbatim
    undercounts every such series and makes it look unverifiable.
    """
    by_series = defaultdict(list)
    for folder_id, label in find_folders():
        try:
            children = list_children(folder_id)
        except RuntimeError as e:
            print(f"WARNING: could not scan {label}: {e}", file=sys.stderr)
            continue
        for f in children:
            art = parse_artifact(f, label)
            if art:
                by_series[series_key(art["title"])].append(art)
    return by_series


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--min-occurrences", type=int, default=2,
                    help="occurrences needed before a series counts as recurring")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        instances = fetch_instances(args.days)
        artifacts = collect_artifacts()
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Group by recurring-series id where Google gives one, else by title. A
    # series whose invite was recreated shows up under several ids, so the
    # title fallback matters more than it looks.
    series = defaultdict(lambda: {"dates": [], "attendees": set(), "titles": set()})
    for ev in instances:
        org = ev.get("organizer") or {}
        if not org.get("self"):
            continue  # not yours to sync, so not yours to map
        dt = (ev.get("start") or {}).get("dateTime")
        if not dt:
            continue
        title = ev.get("summary") or "(untitled)"
        key = ev.get("recurringEventId") or f"title:{series_key(title)}"
        s = series[key]
        s["dates"].append(datetime.fromisoformat(dt).astimezone(timezone.utc))
        s["titles"].add(title)
        for a in ev.get("attendees") or []:
            if a.get("email"):
                s["attendees"].add(a["email"])

    # A series whose invite was recreated gets several recurringEventIds.
    # Merge anything that collapses to the same series key.
    merged = defaultdict(lambda: {"dates": [], "attendees": set(), "titles": set()})
    for s in series.values():
        k = series_key(sorted(s["titles"], key=len)[0])
        merged[k]["dates"].extend(s["dates"])
        merged[k]["attendees"] |= s["attendees"]
        merged[k]["titles"] |= s["titles"]

    rows, excluded = [], []
    for key, s in merged.items():
        dates = sorted(set(s["dates"]))
        title = sorted(s["titles"], key=len)[0]
        norm = normalize_title(title)

        # A personal hold has no attendees; a 1:1 has two counting yourself.
        # Neither belongs in a shared meeting-notes registry, and listing them
        # would put private 1:1 titles in an install report.
        if len(s["attendees"]) == 0:
            excluded.append((title, len(dates), "personal hold, no attendees"))
            continue
        if len(s["attendees"]) <= 2:
            excluded.append((title, len(dates), "1:1"))
            continue
        if len(dates) < args.min_occurrences:
            excluded.append((title, len(dates), "not recurring in this window"))
            continue

        matched = artifacts.get(key, [])
        if not matched:  # tolerate slight title drift between Meet and Calendar
            for other, arts in artifacts.items():
                if titles_match(key, other) or titles_match(norm, other):
                    matched = arts
                    break

        art_dates = sorted({a["meeting_date"] for a in matched})
        rows.append({
            "title": title,
            # The collapsed name, with any per-occurrence month or date label
            # stripped. This is what a registry trigger should key on -- a
            # trigger carrying "August" only ever matches once.
            "series_name": key,
            "recurring_id": None if key.startswith("title:") else key,
            "cadence": cadence_of(dates),
            "occurrences": len(dates),
            "first": dates[0].strftime("%Y-%m-%d"),
            "last": dates[-1].strftime("%Y-%m-%d"),
            "meeting_dates": [d.strftime("%Y-%m-%d") for d in dates],
            "attendees": sorted(s["attendees"]),
            "artifact_dates": art_dates,
            "artifact_count": len(matched),
            "artifact_locations": sorted({a["location"] for a in matched}),
            # No artifacts means nothing will ever sync, regardless of registry.
            "needs_registry_row": bool(art_dates),
        })

    rows.sort(key=lambda r: (not r["needs_registry_row"], r["title"]))
    excluded_counts = defaultdict(int)
    for _, _, reason in excluded:
        excluded_counts[reason] += 1
    result = {
        "window_days": args.days,
        "series": rows,
        "excluded_counts": dict(excluded_counts),
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    mappable = [r for r in rows if r["needs_registry_row"]]
    unrecorded = [r for r in rows if not r["needs_registry_row"]]

    print(f"Recurring series you organize, last {args.days} days: {len(rows)}\n")
    print(f"NEEDS A REGISTRY ROW ({len(mappable)}) "
          f"- recorded, so they can be synced\n")
    for r in mappable:
        print(f"  {r['series_name']}")
        print(f"    seen as       : {r['title']}")
        print(f"    {r['cadence']}, {r['occurrences']} occurrences, "
              f"{r['artifact_count']} artifact(s)")
        print(f"    meeting dates : {' '.join(r['meeting_dates'][-6:])}")
        print(f"    artifact dates: {' '.join(r['artifact_dates'][-6:])}")
        print(f"    location      : {'; '.join(r['artifact_locations']) or '-'}")
        print()

    if unrecorded:
        print(f"NO RECORDINGS ({len(unrecorded)}) - nothing to sync, so no row needed.")
        print("Either the meeting is not recorded, or notes are off for it.\n")
        for r in unrecorded:
            print(f"  {r['title']}  ({r['cadence']}, {r['occurrences']}x)")
        print()

    if excluded:
        by_reason = defaultdict(int)
        for _, _, reason in excluded:
            by_reason[reason] += 1
        print("EXCLUDED (counts only - 1:1 and personal titles stay private):")
        for reason, n in sorted(by_reason.items()):
            print(f"  {reason}: {n}")
        print()

    print("Next: hand this to the skill. It searches ClickUp for each series,")
    print("compares page dates against the artifact dates above, and drafts the")
    print("registry - asking you only about series it cannot reconcile.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
