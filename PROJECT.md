# hermes-agent (fork mss-col) — Hermes Agent

**Repo**: `mss-col/hermes-agent` (fork private) · **Upstream**: `NousResearch/hermes-agent`
**Tujuan**: Hermes Agent — pembantu AI (Una) yang berjalan pada MacBook Boss.

## Struktur remote

| Remote | URL | Peranan |
|---|---|---|
| `origin` | `NousResearch/hermes-agent` | Upstream (hulu) |
| `fork` | `mss-col/hermes-agent` | Fork kita (private) |

## Branch

| Branch | Peranan |
|---|---|
| `local/patches` | **Branch kerja** — patch tempatan kita + sync upstream. Ini yang aplikasi guna. |
| `main` (fork) | Cermin `local/patches` — push `local/patches:main` selepas kerja. |
| `fix/telegram-table-double-star` | Patch double-star (asal). |
| `backup/working-2026-08-29` | Sandaran state sebelum sync upstream 2026-08-29. |

## Patch tempatan kita (WAJIB kekal)

| Patch | Fail | Status upstream |
|---|---|---|
| **double-star table render** | `gateway/platforms/helpers.py` (`_render_table_block`) | ❌ Belum masuk upstream — **perlu kekal** |
| **preflight state.db probe** | `apps/desktop/electron/main.ts` | ❌ Belum masuk upstream — **perlu kekal** |
| ~~nanoid bump~~ | `package.json` | ✅ **Sudah diganti upstream** (3.3.18) — jangan bawa lagi |

## Cara sync dengan upstream (PENTING)

**Guna MERGE, bukan rebase** — rebase menulis semula sejarah dan boleh hilangkan patch kita.

```bash
cd ~/.hermes/hermes-agent
git fetch origin
# Uji dulu pada branch sementara (jangan sentuh local/patches terus)
git checkout -b sync-test local/patches
git merge origin/main
# Selesaikan konflik (package-lock paling mungkin — nanoid)
# SAHKAN patch kita kekal:
grep -c "already carried\|extra wrap" gateway/platforms/helpers.py   # ≥1
grep -c "preflightStateDb" apps/desktop/electron/main.ts             # ≥1
# Bila bersih, apply ke local/patches + push fork
git checkout local/patches && git merge sync-test
git push fork local/patches:main
```

**Semak patch double-star masih relevan** (upstream mungkin sudah fix):
```bash
git show origin/main:gateway/platforms/helpers.py | grep -c "heading.replace\|startswith(\"\*\*\")"
# 0 = upstream belum fix → patch kita perlu kekal
```
*Nota (Lyra verify 2026-08-30): logik double-star kini `core = heading.replace("**","")`
di `helpers.py:383` (commit 951af290, ganti pendekatan `startswith` lama a2abf891).*
*Jangan semak `"already carried"` — bukan marker patch kita.*

## Desktop self-update & branch runtime (PENTING — disahkan 2026-08-30 Una+Lyra)

Desktop "Update now" lari `hermes update --branch <config>`. Branch config dalam
`~/Library/Application Support/Hermes/updates.json` — tiada fail = **default `main`**.

**JANGAN biarkan desktop switch ke `main`** — itu akan bawa checkout keluar dari
`local/patches` dan patch kita padam dari runtime (walaupun kekal di git). Punca
sebenar diselesaikan di `~/.hermes/config.yaml`:

```yaml
updates:
  parked_branch_strategy: update_in_place   # dulu: switch
```

`update_in_place` = checkout TIDAK berganjak; `origin/main` di-merge MASUK ke
branch aktif (fast-forward jika boleh, tag `pre-update-<stamp>` + konflik berhenti
bersih). Jangan set branch desktop ke `local/patches` — upstream tak wujud ref itu,
`resolveHealedBranch` akan tulis balik `main`.

## Ujian (selepas sync)

```bash
# Environment ujian (uv) — perlu extra dev + messaging (aiohttp)
uv sync --extra dev --extra messaging
# Patch double-star
uv run --no-sync python -m pytest tests/gateway/test_table_helpers.py -v
# Patch preflight (typecheck desktop)
npm run --workspace apps/desktop typecheck
```

**Nota**: `tests/gateway/` penuh ada ~15 kegagalan platform-spesifik (systemd/discord/wecom) yang TIDAK boleh jalan pada macOS — bukan regresi. Fokus pada `test_table_helpers` + typecheck.

## Gateway restart

Patch Python tidak aktif sehingga gateway restart (kod dimuat dalam memori). Restart dari shell luar (bukan dari dalam gateway):
```bash
hermes gateway restart
```
