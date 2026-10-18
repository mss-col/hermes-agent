# FASE 2 — BUKTI PATCH KEKAL

Ref: sync-bot = `ef9ec8d909` (tree `7f27d1a53d`) · local/patches = `92b3535cbe` · v0.22.2 = `d923a5eb48` · base v0.21.6 = `818c13be1d`

## (a) merge-tree vs pokok sync-bot
- `git merge-tree --write-tree local/patches v0.22.2` → `259ff9330a4f427740a2ae43ba69065aa6a2849f` (exit 1, 3 konflik — pokok ini MENGANDUNGI penanda konflik).
- Pokok sync-bot → `7f27d1a53ddd21d41c179fe584aeb2ac951c750a`.
- **OID tidak identik — dijangka**, kerana merge ada konflik. Bukti yang bermakna ialah set beza:
  `git diff --stat 259ff9330a sync-bot` = **4 fail sahaja**, 7+/27−:
  `agent/markdown_tables.py` (14), `plugins/platforms/slack/adapter.py` (11), `tools/skill_usage.py` (7)
  = resolusi penanda konflik + `List`→`list`; `gateway/platforms/helpers.py` (2) = buang nombor baris lapuk.
  **Setiap fail lain dalam ~17.9k fail adalah blob-identik dengan hasil merge mekanikal git.**
  Tiada sisipan manual di luar 4 fail yang diisytiharkan dalam FASE-1.

## (b) Blob-hash fail patch
Lajur: base=v0.21.6, up=v0.22.2, ours=local/patches, sb=sync-bot, mt=pokok merge-tree; "upstream ubah" = base≠up.

| Fail | base | up | ours | sb | mt | upstream ubah | sb vs ours | sb vs mt |
|---|---|---|---|---|---|---|---|---|
| PROJECT.md | - | - | 120ce8af8f | 120ce8af8f | 120ce8af8f | tidak | =ours | =mt |
| docs/audit/bukti-sync-0214.md | - | - | 1bedb14d39 | 1bedb14d39 | 1bedb14d39 | tidak | =ours | =mt |
| agent/markdown_tables.py | a3158f8cef | 471f64d522 | 3417ce6731 | 7093f22af8 | f049274e16 | ya | ≠ours | ≠mt (konflik) |
| cron/constants.py | 2c612890c1 | 2c612890c1 | a0ae165637 | a0ae165637 | a0ae165637 | tidak | =ours | =mt |
| gateway/platforms/helpers.py | 8a2a824518 | 398400d5c4 | 8d283807be | 252a6371d0 | 90f08cfcf9 | ya | ≠ours | ≠mt (komen) |
| plugins/kanban/dashboard/plugin_api.py | 0fc7859dc9 | c38f8e399b | 25f33e8779 | 69278f289a | 69278f289a | ya | ≠ours | =mt |
| plugins/platforms/slack/adapter.py | 28a152fe30 | 5fd44180e8 | 952ad42819 | 6577fa78f2 | 05bea16f7d | ya | ≠ours | ≠mt (konflik) |
| tools/skill_usage.py | f5ce237945 | 0eab4f685f | 25fd967e04 | 0ca63d85a6 | 5c63636f7a | ya | ≠ours | ≠mt (konflik) |
| tests/agent/test_markdown_tables.py | ada3063b25 | ada3063b25 | 2b3c806d80 | 2b3c806d80 | 2b3c806d80 | tidak | =ours | =mt |
| tests/cron/test_claim_job_for_fire.py | af958bc9ee | d4bf696eb9 | ca07692326 | db71acac4f | db71acac4f | ya | ≠ours | =mt |
| tests/cron/test_local_fire_claim_ttl_patch.py | - | - | adbbe2326a | adbbe2326a | adbbe2326a | tidak | =ours | =mt |
| tests/gateway/test_table_helpers.py | ae95dee519 | ae95dee519 | 1b2bf01015 | 1b2bf01015 | 1b2bf01015 | tidak | =ours | =mt |
| tests/plugins/test_kanban_done_sort_patch.py | - | - | 4d7416595b | 4d7416595b | 4d7416595b | tidak | =ours | =mt |
| tests/tools/test_skill_usage.py | fb9c95f8b3 | fb9c95f8b3 | c200f5876c | c200f5876c | c200f5876c | tidak | =ours | =mt |

**Keadaan dijangka dipenuhi:** fail yang upstream tidak sentuh → sb == ours (9/9). Fail yang upstream
ubah → sb == upstream + patch kita (≠ours dijangka).

**Bukti kandungan patch (lebih kuat daripada hash):** `diff <(git diff --numstat v0.21.6 local/patches) <(git diff --numstat v0.22.2 sync-bot)`
→ **IDENTIK** (14 fail, +684/−15 kedua-dua). Perbandingan baris +/− per fail (`git diff -U0`, tanpa konteks):
skill_usage.py, kanban plugin_api.py, test_claim_job_for_fire.py → **identik baris demi baris**.
Beza hanya: markdown_tables.py `List[str]`→`list[str]` (3 baris), slack adapter baris "−" kini
`removeprefix/removesuffix` (kod upstream yang diganti, bukan kod kita), helpers.py komen `:281` dibuang.

## (c) Penanda (git show sync-bot:<f> | grep -c)
| Fail | Penanda | Jangka | Dapat | |
|---|---|---|---|---|
| tools/skill_usage.py | `usage.json.corrupt` | 2 | 2 | OK |
| plugins/kanban/dashboard/plugin_api.py | `_completed_at_sort_value` | 2 | 2 | OK |
| cron/constants.py | `^FIRE_CLAIM_TTL_SECONDS = 1800$` | 1 | 1 | OK |
| cron/jobs.py | `^FIRE_CLAIM_TTL_SECONDS = ` | 0 | 0 | OK |
| gateway/platforms/helpers.py | `heading.replace` | 1 | 1 | OK |
| agent/markdown_tables.py | `_split_unescaped_pipes` | 2 | 2 | OK |
| tests/gateway/test_table_helpers.py | `no_double_star` | 2 | 2 | OK |
| plugins/platforms/slack/adapter.py | `return split_table_row(line)` | 1 | 1 | OK |

(Nota: PROJECT.md menyebut "4 ujian `no_double_star`" — grep -c memberi 2 baris di local/patches juga; bukan regresi, penerangan PROJECT.md tidak tepat.)

## (d) Kiraan baris
- Patch kita merentas fail (`git diff --shortstat v0.22.2 sync-bot`): **14 fail, +684 / −15** (sama seperti v0.21.6..local/patches).
- Pengambilan upstream (`git diff --shortstat local/patches...sync-bot`): 4987 fail, +126572 / −45104.
