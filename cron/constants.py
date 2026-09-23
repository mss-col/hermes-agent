"""Fire-claim timing bounds shared by the job store and its siblings.

Import-free on purpose: a sibling loaded fresh from a newer on-disk tree must resolve
these without going through the ``cron.jobs`` object a long-lived process cached at boot.
"""

# A fire_claim younger than this is a live run (heartbeat cadence is 60 s). One value
# for claiming, one-shot re-arm, and stale-error recovery so they cannot disagree.
#
# PATCH LOKAL (Una, 2026-09-22): 300 -> 1800. Reason: the watchdog timeout is an
# INACTIVITY limit (HERMES_CRON_TIMEOUT, default 600s), not a wall-clock cap, so a healthy
# run may legitimately exceed 300s of wall clock while polling an external tool for approval.
# Measured on this host: 3 of 18 runs of a 5-minute monitor job took 13.3/21.2/23.8 min; each
# one lost ownership and the next tick re-anchored on the run's END, leaving 19-29 min
# unmonitored. 1800 matches ONESHOT_RUN_CLAIM_TTL_SECONDS in cron/jobs.py for the same
# reason. Raising this does NOT delay reclaim of a dead owner: _claim_owner_is_dead() releases
# the claim immediately when the claiming pid is gone, so the TTL only covers unprovable cases.
#
# Value lives HERE, not in cron/jobs.py: upstream moved the constant to this import-free
# module (v0.21.4) so a sibling loaded fresh from a newer tree resolves it without the
# cron.jobs object a long-lived process cached at boot. A duplicate in jobs.py would split
# the value — jobs.py would see the patched number while cron/occurrences.py saw the old one.
FIRE_CLAIM_TTL_SECONDS = 1800
# A hosted/webhook fire for the armed slot can arrive a few seconds before the stored
# ``next_run_at`` (the fire scheduler's clock runs ahead of ours). Claims that early still own
# the slot; only claims further ahead are off-tick manual/dashboard fires.
FIRE_CLAIM_SKEW_SECONDS = 60
# Multiplier over HERMES_CRON_TIMEOUT for claim TTLs: the timeout is an *inactivity* limit, not a
# wall-clock cap, so healthy runs may legitimately exceed it and a TTL of exactly the timeout
# would expire live claims.
CLAIM_TTL_INACTIVITY_HEADROOM = 3
