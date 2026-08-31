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

| Patch | Fail | Status upstream | Semak relevan (0 = belum fix → perlu kekal) |
|---|---|---|---|
| **double-star table render** | `gateway/platforms/helpers.py` (`_render_table_block`) | ❌ Belum masuk upstream — **perlu kekal** | `git show origin/main:gateway/platforms/helpers.py \| grep -c 'heading.replace'` |
| **preflight state.db probe** | `apps/desktop/electron/main.ts` | ❌ Belum masuk upstream — **perlu kekal** | `git show origin/main:apps/desktop/electron/main.ts \| grep -c "Checking the local database before continuing"` |
| **sandbox CA fix (npm SSLEOFError)** | `scripts/sandbox/stage2-run.sh` | ❌ Belum masuk upstream — **perlu kekal** | `git show origin/main:scripts/sandbox/stage2-run.sh \| grep -c "NODE_EXTRA_CA_CERTS /work/certs/ca.pem"` |
| **db_probe catch DatabaseError** | `scripts/db_integrity_probe.py` | ❌ Fail tak wujud di upstream — **perlu kekal** | `git cat-file -e origin/main:scripts/db_integrity_probe.py` (gagal = belum wujud) |
| **npm debug log on failure** | `scripts/install.sh` | ❌ Belum masuk upstream — **perlu kekal** | `git show origin/main:scripts/install.sh \| grep -c "npm debug log"` |
| **proxy host+stage tags** | `scripts/sandbox/proxy.py` | ❌ Belum masuk upstream — **perlu kekal** | `git show origin/main:scripts/sandbox/proxy.py \| grep -c "read-request\|parse-request\|serve-fixture\|https-upstream\|tls-handshake"` |
| **collect npm logs in E2E** | `tests/install/install-update-e2e.sh` | ❌ Belum masuk upstream — **perlu kekal** | `git show origin/main:tests/install/install-update-e2e.sh \| grep -c "npm-logs"` |
| ~~nanoid bump~~ | `package.json` | ✅ **Sudah diganti upstream** (3.3.18) — jangan bawa lagi | — |

**Cara semak setiap patch masih relevan** (sebelum setiap sync): jalankan arahan "Semak relevan" di atas. Jika output ≥1, upstream sudah fix → **buang patch kita** (jangan bawa lagi di cycle seterusnya). Jika 0, patch kita perlu kekal.

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
