# FASE 4 — VALIDASI DIRI (Opus)

## (1) Baca semula SEMUA resolusi konflik vs kod v0.22.2 sebenar
| Fail | Keputusan | Penilaian semula Opus |
|---|---|---|
| agent/markdown_tables.py | KEKALKAN + `list[str]` | v0.22.2:agent/markdown_tables.py:31-33 masih `.split("|")` naif; satu-satunya commit upstream = `d76cce4f11` (autofix anotasi). Penulisan semula = tidak perlu. Betul. |
| plugins/platforms/slack/adapter.py | KEKALKAN + `list[str]` | v0.22.2 :184-189 masih naif (hanya `removeprefix`, FURB188). `block_kit.py::_split_row` mengendali `\|` tetapi itu laluan Block Kit sahaja (blob sama sejak v0.21.6) — tidak meliputi `format_message`/`_wrap_markdown_tables`. Mewakilkan ke helper kongsi = konsisten dengan upstream `gateway/platforms/helpers.py` yang sudah berbuat sama. Betul. |
| tools/skill_usage.py | KEKALKAN + `dict[...]` | v0.22.2 `load_usage` masih `logger.debug` + `return {}`; penulis `_locked_update` (sync-bot :418) memuat → op → simpan, jadi fail korup = kehilangan data senyap. Betul. |
| (luar konflik) gateway/platforms/helpers.py komen | Buang `:281` | Rujukan sebenar kini telegram/adapter.py:404. Betul (komen sahaja). |
3 sub-agen Sonnet bebas mencapai resolusi teks yang sama; satu meramal blob skill_usage `0ca63d85a6` = blob sync-bot.
**Tiada keputusan BUANG pada sync ini** — setiap patch masih 0 penanda di v0.22.2.

## (2) Tiga titik risiko tertinggi — diuji sendiri
| # | Risiko | Ujian Opus | Keputusan |
|---|---|---|---|
| R1 | **Separuh Slack patch tiada ujian** (kalau hunk hilang, semua ujian sedia ada lulus) | Ujian sementara 3 kes (`_split_table_row`, `_align_table`, `_wrap_markdown_tables` E2E) dalam eksport `tests/gateway/test_f4_slack_escaped_pipe_tmp.py` (TIDAK di-commit) | sync-bot 3/3 lulus; Slack `_split_table_row` = v0.22.2 → **0/3 (3 gagal)**; `tests/gateway/test_slack.py` + ujian sementara = 218 lulus, 0 gagal, 1 langkau |
| R2 | TTL berpecah antara `cron.jobs` & sibling (`cron/occurrences.py` import terus dari constants) | Import runtime dari eksport | `constants=1800`, `jobs=1800`, objek sama (`is` True), lalai `claim_job_for_fire(claim_ttl_seconds)=1800`; satu-satunya definisi bukan-ujian = cron/constants.py:23; tiada ujian upstream baharu yang hardcode 300/301 |
| R3 | Backup korup tidak berfungsi melalui laluan penulis upstream baharu | E2E `scripts/e2e_skill_usage.py`: HERMES_HOME sementara, `.usage.json` korup mengandungi `pinned-skill`, panggil `bump_use("other-skill")` | sync-bot: WARNING dilog, `.usage.json.corrupt-20261018-094505` = kandungan asal (True). **v0.22.2 tulen: tiada backup, `pinned-skill` hilang senyap** → patch masih perlu dan berfungsi |

## (3) Senarai patch PROJECT.md lama vs pokok baharu
| Patch PROJECT.md | Status sync-bot |
|---|---|
| double-star table render (helpers.py) | KEKAL — `heading.replace` 1 (:326) |
| backup corrupt `.usage.json` | KEKAL — 2 penanda (:373, :386) |
| ujian regresi double-star | KEKAL — blob `1b2bf01015` = local/patches |
| pipe GFM escaped (markdown_tables + slack) | KEKAL — kedua-dua separuh |
| FIRE_CLAIM_TTL 1800 (constants.py) | KEKAL — :23; jobs.py definisi 0 |
| done-column sort koersi (kanban) | KEKAL — :181 def, :361 guna |
| inventori PROJECT.md | KEKAL — blob `120ce8af8f` tidak berubah |
| ~~preflight state.db~~ | masih diatasi: `apps/desktop/electron/updater/state-db-preflight.ts` ADA (throw = gagal-ditutup :25/:37/:60), `hermes_cli/backup_sqlite.py` ADA (`quick_check`) |
| ~~db_probe~~ | `scripts/db_integrity_probe.py` tiada — betul |
| ~~npm debug log~~ | `scripts/build/node-deps.mjs` ADA, `stdio: 'inherit'` :77/:165 |
| ~~sandbox ×3~~ | `scripts/sandbox/stage2-run.sh`, `proxy.py`, `tests/install/install-update-e2e.sh` tiada — betul |
| ~~nanoid bump~~ | package-lock nanoid 6.0.0 (≥3.3.18) — betul |
`git diff --numstat v0.21.6 local/patches` ≡ `git diff --numstat v0.22.2 sync-bot` (14 fail, +684/−15). **Tiada patch hilang senyap.**

## (4) git log --oneline -5 sync-bot
```
ef9ec8d909 merge: sync upstream v0.22.2 (stable, 3760 commit)
d923a5eb48 Release 0.22.2 from release/0.22.1 with the published v0.22.1 as a parent
4ccc58062c Merge pull request #138560 from NousResearch/fix/local-laptop-hardening
4ac844ef4a Merge pull request #138594 from NousResearch/fix/host-record-recycled-pid-0.22.1
297552a9d6 fix(compression): fallback summaries, multiline setup notes and parallel loads keep skill markers right
```
Merge commit `ef9ec8d909`, induk `92b3535cbe` (local/patches) + `d923a5eb48` (v0.22.2).

## (5) Kawalan negatif (6/6 diskriminatif) — `scripts/negctl.sh`, log `f4-negctl.log`
Kaedah: dalam eksport scratch, ganti fail sumber dengan blob v0.22.2 (= blok patch dibuang, hash disahkan) → jalankan ujian → pulihkan blob sync-bot (hash disahkan) → jalankan semula.
| Fail sumber dibuang patch | Ujian | NEGATIF | POSITIF selepas pulih |
|---|---|---|---|
| cron/constants.py | test_local_fire_claim_ttl_patch.py | 2 lulus / **2 gagal** | 4/0 |
| tools/skill_usage.py | test_skill_usage.py | 26 / **2 gagal** | 28/0 |
| agent/markdown_tables.py | test_markdown_tables.py | 6 / **2 gagal** | 8/0 |
| gateway/platforms/helpers.py | test_table_helpers.py | 5 / **4 gagal** | 9/0 |
| plugins/kanban/dashboard/plugin_api.py | test_kanban_done_sort_patch.py | 0 / **16 gagal** | 16/0 |
| plugins/platforms/slack/adapter.py | test_f4_slack_escaped_pipe_tmp.py (sementara) | 0 / **3 gagal** | 3/0 |

## Insiden proses (dilaporkan dengan jujur)
- Cubaan pertama kawalan negatif guna pemboleh ubah shell sebagai arahan; shell zsh tidak memecahnya, `git show` tidak berjalan tetapi redirect `>` **mengosongkan 5 fail dalam eksport scratch** `/tmp/sync-v0.22.2/export` (bukan repo, bukan worktree sync-bot). Keputusan larian itu dibuang (tidak sah). Kelima-lima fail dipulihkan dari blob sync-bot dan disahkan `git hash-object` = `git rev-parse sync-bot:<f>` sebelum larian semula yang sah di atas. Worktree `wt` dan repo utama: `git status` bersih.
- Ujian R3 (`tempfile.mkdtemp`) mencipta 2 direktori di luar `/tmp/sync-v0.22.2/`: `/tmp/hh-3dghpuwl`, `/tmp/hh-h11hf7jg` (HERMES_HOME sementara, mengandungi `skills/.usage.json*` ujian sahaja). Tidak dipadam (G1) — lihat CHECKPOINT BOSS.
