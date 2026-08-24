#!/usr/bin/env python3
"""Tests for the scan cutoff.

This logic gets its own test because getting it wrong loses work silently:
an artifact filtered out by the cutoff never enters `processed`, so nothing
downstream notices it is missing. No error, no digest line, no retry.

Run: python test_cutoff.py
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scan_sources import compute_cutoff, LOOKBACK  # noqa: E402

NOW = datetime(2026, 8, 21, 3, 0, tzinfo=timezone.utc)
failures = []


def check(name, got, want):
    if got == want:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}\n          got  {got}\n          want {want}")
        failures.append(name)


def check_true(name, cond, detail=""):
    if cond:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name}  {detail}")
        failures.append(name)


print("compute_cutoff")

# The bug this fix exists for: an artifact created shortly BEFORE last_run but
# never processed must still be scanned, or it is lost forever.
last_run = "2026-08-20T03:00:00+00:00"
cutoff = compute_cutoff(None, last_run, False, now=NOW)
stranded = datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)  # before last_run
check_true(
    "artifact created before last_run is still scanned",
    stranded >= cutoff,
    f"cutoff={cutoff} stranded={stranded}",
)

check(
    "cutoff is last_run minus the lookback",
    cutoff,
    datetime(2026, 8, 20, 3, 0, tzinfo=timezone.utc) - LOOKBACK,
)

# Anything older than the buffer is still excluded - the window is bounded.
ancient = datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc)
check_true("artifact older than the buffer is excluded", ancient < cutoff)

# A naive last_run must not blow up on comparison with tz-aware Drive times.
naive = compute_cutoff(None, "2026-08-20T03:00:00", False, now=NOW)
check_true("naive last_run is treated as UTC", naive.tzinfo is not None)
check("naive and aware last_run agree", naive, cutoff)

# --since overrides last_run exactly, with no buffer applied.
check(
    "--since wins over last_run and takes no buffer",
    compute_cutoff("2026-07-01", last_run, False, now=NOW),
    datetime(2026, 7, 1, tzinfo=timezone.utc),
)

# --all ignores last_run and falls back to the default window.
check(
    "--all falls back to the 14-day window",
    compute_cutoff(None, last_run, True, now=NOW),
    NOW - timedelta(days=14),
)

# No state at all - first run.
check(
    "no last_run falls back to the 14-day window",
    compute_cutoff(None, None, False, now=NOW),
    NOW - timedelta(days=14),
)

print()
if failures:
    print(f"{len(failures)} FAILED: {', '.join(failures)}")
    sys.exit(1)
print("all passed")
