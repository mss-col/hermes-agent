# FASE 3 — UJIAN

## Persekitaran
- Pokok diuji: **eksport `git archive sync-bot`** → `/tmp/sync-v0.22.2/export` (bukan worktree home — Perangkap #12 dielak).
  Garis dasar: `git archive v0.22.2` → `/tmp/sync-v0.22.2/export-upstream`.
- Interpreter: `/Users/mss/.hermes/hermes-agent/venv/bin/python` = Python **3.14.8**, pytest **9.1.1** (ada → tidak perlu fallback python3.13).
- Resolusi import disahkan dari eksport, bukan editable install:
  `cron/constants.py`, `agent/markdown_tables.py`, `tools/skill_usage.py` → `/private/tmp/sync-v0.22.2/export/...`; `FIRE_CLAIM_TTL_SECONDS` = 1800.
- Runner: `scripts/run_tests.sh` (AGENTS.md: jangan pytest kosong), `HERMES_PYTHON=<venv python>`, TZ=UTC, env bersih, -j 8.
  Amaran `fatal: not a git repository` pada pre-compile = dijangka untuk eksport `git archive` (tiada `.git`), tidak menjejaskan ujian.
- Node v26.7.0, npm 11.19.1 (`~/.hermes/node/bin`), memenuhi `engines` package.json.

## Keputusan
| # | Suite | Arahan | Exit | Lulus | Gagal | Langkau | Log |
|---|---|---|---|---|---|---|---|
| 1 | Ujian patch (6 fail) | `run_tests.sh tests/cron/test_local_fire_claim_ttl_patch.py tests/cron/test_claim_job_for_fire.py tests/plugins/test_kanban_done_sort_patch.py tests/tools/test_skill_usage.py tests/agent/test_markdown_tables.py tests/gateway/test_table_helpers.py` | **0** | **85** | 0 | 0 | f3-patch-tests.log |
| 2 | `tests/cron/` PENUH | `run_tests.sh tests/cron/` | **0** | **1476** | **0** | 13 | f3-cron-full.log |
| 3 | Ujian rakan (58 fail yang merujuk kod ditampal: markdown_tables / slack / table helpers / skill_usage / kanban dashboard / curator) | `xargs run_tests.sh < f3-related-files.txt` | 1 | 2297 | 14 | 2 | f3-related.log |
| 4 | Garis dasar v0.22.2 tulen bagi 2 fail yang gagal di #3 | `run_tests.sh tests/pm/test_workspace_build_inputs.py tests/hermes_state/test_hermes_state.py` (dalam export-upstream) | 1 | 291 | **14** | 0 | f3-baseline-upstream.log |
| 5 | `npm ci` di ROOT repo (eksport) | `npm ci --no-audit --no-fund` | **0** | 1344 pakej | — | — | f3-npm-ci.log |
| 6 | Typecheck desktop | `( cd apps/desktop && npm run typecheck )` (4× tsc) | **0** | — | — | — | f3-typecheck.log |

Per-fail suite #1: ttl_patch 4✓, markdown_tables 8✓, kanban_done_sort_patch 16✓, table_helpers 9✓, claim_job_for_fire 20✓, skill_usage 28✓.

## Klasifikasi 14 kegagalan (#3)
Set `FAILED` sync-bot vs v0.22.2 tulen: `diff fail-upstream.txt fail-syncbot.txt` → **IDENTIK** (14 = 14, nama ujian sama).
→ **Bukan regresi patch** (kod upstream tulen gagal sama; fail ini tidak menyentuh mana-mana fail patch).
| Fail | Bil | Punca | Kelas |
|---|---|---|---|
| tests/pm/test_workspace_build_inputs.py | 6 | `AssertionError: saved backend replay test requires real uv` — `uv` sebenar tiada dalam env bersih runner | persekitaran / alat (bukan plugin, bukan patch) |
| tests/hermes_state/test_hermes_state.py | 8 | TestVacuum / TestAutoMaintenance / TestConnectionLifecycle: `assert False is True` pada laluan VACUUM/maintenance SQLite | platform-macOS / build SQLite Python 3.14 tempatan — upstream sama |

Fail ini masuk senarai #3 hanya kerana grep `skill_usage`/`plugin_api` (rujukan rentas), bukan kerana bergantung pada patch.

## Ruff (dari F1)
`ruff check --config ruff.toml` pada 6 fail patch Python → All checks passed (exit 0).
