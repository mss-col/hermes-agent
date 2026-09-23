"""Regression tests for the local FIRE_CLAIM_TTL_SECONDS patch (Una, 2026-09-22).

Why this file exists: the patch raises the fire-claim TTL from 300s to 1800s. In
v0.21.4 upstream MOVED the constant out of ``cron/jobs.py`` into the import-free
``cron/constants.py`` (so a sibling module loaded fresh from a newer tree resolves
it without the cached ``cron.jobs`` object). A merge that keeps the old local
assignment in ``jobs.py`` is silent-rot: ``cron/jobs.py`` would read the patched
1800 while ``cron/occurrences.py`` (which imports from ``cron.constants``) kept
300 — two disagreeing TTLs for the same claim, with nothing failing.

These tests are deliberately DISCRIMINATIVE: drop the patch and they fail.
"""

from __future__ import annotations

import cron.constants
import cron.jobs


def test_fire_claim_ttl_is_the_patched_value():
    # 300 (upstream default) is too short: HERMES_CRON_TIMEOUT is an INACTIVITY
    # limit, not a wall-clock cap, so a healthy run polling for approval can
    # exceed it and lose claim ownership.
    assert cron.constants.FIRE_CLAIM_TTL_SECONDS == 1800


def test_jobs_reexports_the_same_value_as_constants():
    # The value must resolve through cron.constants — the single source of truth.
    assert cron.jobs.FIRE_CLAIM_TTL_SECONDS == cron.constants.FIRE_CLAIM_TTL_SECONDS


def test_no_stale_duplicate_definition_in_jobs_module():
    # Guard against a merge re-introducing a local assignment: that splits the
    # value across modules instead of raising an error.
    import inspect

    source = inspect.getsource(cron.jobs)
    assert "\nFIRE_CLAIM_TTL_SECONDS = " not in source, (
        "cron/jobs.py must IMPORT FIRE_CLAIM_TTL_SECONDS from cron.constants, "
        "not define its own copy (a duplicate silently splits the value)"
    )


def test_ttl_exceeds_the_default_inactivity_timeout():
    # The behavioural intent: the TTL must outlast a default 600s inactivity
    # window, otherwise a run that simply waits >300s loses its claim.
    assert cron.constants.FIRE_CLAIM_TTL_SECONDS >= cron.jobs._DEFAULT_CRON_INACTIVITY_TIMEOUT
