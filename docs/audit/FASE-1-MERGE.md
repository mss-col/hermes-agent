# FASE 1 — SYNC local/patches → v0.22.2

Tarikh: 2026-10-18 · Orkestrator: Opus (penulis tunggal resolusi + commit)

## Keadaan awal (disahkan)
- `local/patches` = `92b3535cbe012f0a1014d741a4651a92d97c05ba`, tree bersih.
- `v0.22.2^{commit}` = `d923a5eb487a17c0a68801bba9ef0f56c81040a8`.
- merge-base = `818c13be1d` (= tag v0.21.6). `git rev-list --count v0.21.6..v0.22.2` = 3760.
- Branch `sync-bot` TIDAK wujud sebelum ini → `git branch -D` tidak perlu (tiada pemadaman).
- Gateway tidak berjalan (`pgrep -f 'hermes_cli.main gateway run'` kosong).

## Penyimpangan prosedur (sengaja, demi keselamatan)
`~/.hermes/hermes-agent` ialah **pemasangan hidup** (editable install venv, desktop). `git checkout`
di sana akan menukar 17,916 fail runtime ke tree separa-merge (penanda konflik). Maka branch
`sync-bot` dicipta melalui **worktree** `/tmp/sync-v0.22.2/wt`:
`git worktree add -b sync-bot /tmp/sync-v0.22.2/wt local/patches` → `git merge --no-edit v0.22.2`.
Branch, commit dan sejarah adalah identik dengan prosedur asal; checkout utama kekal
`local/patches` @ 92b3535cbe (status bersih, disahkan selepas commit).

## Hasil merge
Konflik = tepat 3 fail seperti dijangka (tiada konflik luar senarai):
`agent/markdown_tables.py`, `plugins/platforms/slack/adapter.py`, `tools/skill_usage.py`.
Auto-merge bersih: `gateway/platforms/helpers.py`, `plugins/kanban/dashboard/plugin_api.py`,
`tests/cron/test_claim_job_for_fire.py`.

Merge commit: **`ef9ec8d9094257ae2159db7ce1962dec5e302c71`** (tree `7f27d1a53ddd21d41c179fe584aeb2ac951c750a`),
induk = `92b3535cbe` (local/patches) + `d923a5eb48` (v0.22.2).

## Relevansi patch terhadap v0.22.2 (penanda diskriminatif, `git show v0.22.2:<f> | grep -c`)
| Patch | Penanda | v0.22.2 | local/patches |
|---|---|---|---|
| double-star | `heading.replace` @ gateway/platforms/helpers.py | 0 | 1 |
| corrupt usage backup | `usage.json.corrupt` @ tools/skill_usage.py | 0 | 2 |
| ujian double-star | `no_double_star` @ tests/gateway/test_table_helpers.py | 0 | 2 |
| pipe GFM escaped | `_split_unescaped_pipes` @ agent/markdown_tables.py | 0 | 2 |
| TTL 1800 | `^FIRE_CLAIM_TTL_SECONDS = 1800$` @ cron/constants.py | 0 (upstream `= 300`, baris 9) | 1 |
| kanban sort | `_completed_at_sort_value` @ plugins/kanban/dashboard/plugin_api.py | 0 | 2 |

→ **Tiada satu pun patch diatasi upstream. Tiada "BUANG patch lapuk" pada sync ini.**
Upstream v0.22.2 load_usage masih `logger.debug(...)` + `return {}` (v0.22.2:tools/skill_usage.py, fungsi `load_usage`);
split_table_row masih `.split("|")` naif; slack `_split_table_row` masih `s.split("|")`.

## Keputusan per konflik
Punca ketiga-tiga konflik **sama**: upstream jalankan pembaikan linter automatik
(`d76cce4f11 ci: apply all automatic linter fixes`, `32b70e9733 FURB188`, `2ff58849f4 UP037`) yang
menukar `List[...]`/`Dict[...]` → `list[...]`/`dict[...]` dan `s[1:] if startswith` → `removeprefix`.
`ruff.toml` v0.22.2 mengaktifkan `UP006` → mengekalkan `List[str]` dalam patch kita = kegagalan lint.

| Fail | Keputusan | Bukti (sync-bot) |
|---|---|---|
| agent/markdown_tables.py | **KEKALKAN patch, diadaptasi**: badan `split_table_row` kita + tandatangan `-> list[str]` upstream. Helper auto-merge `_split_unescaped_pipes` turut ditukar `List`→`list` (UP006). | `_is_escaped` :26, `_split_unescaped_pipes` :36, `split_table_row` :58 |
| plugins/platforms/slack/adapter.py | **KEKALKAN patch, diadaptasi**: `_split_table_row` mewakilkan ke `agent.markdown_tables.split_table_row`; tandatangan `-> list[str]`. Versi upstream `removeprefix/removesuffix + split("|")` = tingkah laku naif yang sama yang patch kita betulkan. | import :40, `_split_table_row` :185, `return split_table_row(line)` :192 |
| tools/skill_usage.py | **KEKALKAN patch, diadaptasi**: docstring + blok backup/WARNING kita; tandatangan `-> dict[str, dict[str, Any]]`. `datetime` masih diimport upstream (:15). | `load_usage` :369, backup `.usage.json.corrupt-<ts>` :386, `logger.warning` :389/:394 |

Teks akhir: `git diff v0.22.2 sync-bot -- <3 fail>` = tepat patch asal kita, beza hanya anotasi jenis.

## Adaptasi tambahan (luar konflik)
- `gateway/platforms/helpers.py:282` — komen patch merujuk `plugins/platforms/telegram/adapter.py:281`;
  di v0.22.2 import itu di **:404** (`convert_table_to_bullets as _wrap_markdown_tables`), dipanggil :5629.
  Nombor baris dibuang (rujukan fail sahaja) supaya tidak reput lagi. Dakwaan "tiada renderer
  Telegram berasingan" masih benar (telegram/adapter.py:402 komen upstream).

## Semakan SEMUA fail senarai patch PROJECT.md (bukan hanya 3 konflik)
`git diff --stat v0.22.2 sync-bot` = **14 fail, +684/−15** — sama bilangan fail & baris dengan
`git diff --stat v0.21.6 local/patches` (14 fail, +684/−15). Tiada fail patch tercicir.
| Fail | Status di sync-bot |
|---|---|
| gateway/platforms/helpers.py | patch hadir (`core = heading.replace` :326), `_render_table_block` :300 dipanggil :349 |
| tools/skill_usage.py | hadir (lihat di atas) |
| tests/gateway/test_table_helpers.py | hadir (`no_double_star` ×2) |
| agent/markdown_tables.py + slack adapter | hadir |
| cron/constants.py | `FIRE_CLAIM_TTL_SECONDS = 1800` :23 (satu-satunya); `cron/jobs.py` definisi tempatan = **0**; jobs.py :32 mengimport dari constants; cron/occurrences.py :86 juga import dari constants |
| tests/cron/test_claim_job_for_fire.py | `jobs.FIRE_CLAIM_TTL_SECONDS + 1` :152 |
| plugins/kanban/dashboard/plugin_api.py | `_completed_at_sort_value` :181, dipakai dalam sort lajur done :361 (tidak yatim) |
| tests: test_local_fire_claim_ttl_patch.py, test_kanban_done_sort_patch.py, test_markdown_tables.py (+3), test_skill_usage.py (+2) | hadir |
| PROJECT.md, docs/audit/bukti-sync-0214.md | dokumen kita, hadir tanpa ubah |

Rasional TTL masih sah di v0.22.2: `ONESHOT_RUN_CLAIM_TTL_SECONDS = 1800` (cron/jobs.py:204);
`_claim_is_live` (cron/jobs.py:2231) → `return not _claim_owner_is_dead(claim)` (:2242),
`_claim_owner_is_dead` kini di cron/scheduler_ownership.py:151 (dipindah upstream, masih diwayarkan).

## Lint
`ruff check --config ruff.toml` (ruff 0.15.6) pada 6 fail patch Python → **All checks passed!** (exit 0).

## Semak silang sub-agen
Lihat seksyen di hujung (ditambah selepas laporan penganalisis Sonnet tiba).

## Semak silang sub-agen (3 × Sonnet, baca-sahaja, selari) — disahkan Opus
| Fail | Verdict sub-agen | Padan resolusi Opus? | Bukti semakan |
|---|---|---|---|
| tools/skill_usage.py | KEKALKAN, adaptasi `dict[...]`; upstream hanya autofix ruff (`d76cce4f11`, `9eab688b42`); tiada quarantine `.usage.json` di v0.22.2 (`load_usage` masih `logger.debug` + `{}`); storan tidak berpindah (`_usage_file()` = `get_hermes_home()/skills/.usage.json`) | **YA** — sub-agen meramal blob `0ca63d85a6503db33fbfcd19e80731552bbe8a0a`; `git rev-parse sync-bot:tools/skill_usage.py` = `0ca63d85a6` ✔ | FASE-2 jadual (b) |
| plugins/platforms/slack/adapter.py | KEKALKAN, adaptasi `list[str]`; upstream hanya `d76cce4f11` + FURB188 `32b70e9733`; v0.22.2 :189 masih `.split("|")`; buktikan bug wujud di v0.22.2 (5 lajur bukannya 3) | **YA** — teks sama | sync-bot :185-192 |
| agent/markdown_tables.py | KEKALKAN, adaptasi; tukar juga :36/:41/:42 `List`→`list` (kalau tidak 4× UP006); biarkan `from typing import List` :15 (F401/UP035 dimatikan ruff.toml) | **YA** — teks sama, termasuk 3 baris luar hunk | ruff exit 0 |

Temuan tambahan sub-agen (diambil ke F4/risiko):
- **Jurang liputan:** tiada ujian meliputi separuh Slack patch — kalau hunk Slack hilang, semua ujian sedia ada tetap lulus. → diuji sendiri di F4.
- `test_split_even_backslashes_before_pipe_still_delimits` lulus pada upstream juga (pengawal regresi, bukan diskriminatif).
- Pengerasan pilihan skill_usage (bukan skop merge): `OSError` turut menamakan semula fail sah yang sekadar tidak boleh dibaca; `UnicodeDecodeError` tidak ditangkap; nama backup resolusi 1 saat boleh berlanggar.
- `~/.hermes/AGENTS.md` G2 kata venv Python 3.11 — realiti 3.14.8 (lapuk, G8).
