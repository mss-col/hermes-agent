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
git show origin/main:gateway/platforms/helpers.py | grep -c "startswith(\"\*\*\")"
# 0 = upstream belum fix → patch kita perlu kekal
```

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
