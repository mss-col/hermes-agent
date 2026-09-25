"""Ujian regresi untuk tampalan tempatan 10 — koersi ``completed_at`` lajur "done".

PUNCA (dijumpai 2026-09-24, belum dibetulkan hulu setakat v0.21.5):
    ``get_board()`` menyusun lajur "done" guna kunci
    ``(completed_at is None, -(completed_at or 0))``. Lajur itu BIASA mengandungi
    cap masa unix (int), tetapi baris lama boleh menyimpan nilai ISO/teks. Python
    membaling ``TypeError: bad operand type for unary -: 'str'`` semasa menyusun,
    dan itu memecahkan SELURUH respons papan — bukan sekadar satu kad.

TAMPALAN: ``_completed_at_sort_value()`` mengoersi None/bool/int/float/str ke int;
teks tidak sah menjadi 0.

⚠ Ujian ini DISKRIMINATIF: ia mesti GAGAL tanpa tampalan. Sahkan dengan
mengembalikan kunci lama — ``TypeError`` akan muncul dan ujian merah.
"""
from __future__ import annotations

import pytest


def _plugin():
    """Import modul plugin dashboard kanban (bukan pakej yang diimport automatik)."""
    from plugins.kanban.dashboard import plugin_api

    return plugin_api


# ---------------------------------------------------------------------------
# Pembantu murni
# ---------------------------------------------------------------------------


def test_helper_exists_and_is_callable():
    # Tanpa tampalan, nama ini tidak wujud langsung di hulu.
    pa = _plugin()
    assert callable(pa._completed_at_sort_value)


@pytest.mark.parametrize(
    "nilai,jangkaan",
    [
        (None, 0),
        (0, 0),
        (1_700_000_000, 1_700_000_000),
        (1_700_000_000.9, 1_700_000_000),   # float dipotong, bukan dibundar
        ("1700000000", 1_700_000_000),      # teks angka sah
        ("1700000000.5", 1_700_000_000),    # teks float sah
        ("bukan angka", 0),                 # teks tidak sah -> 0, BUKAN baling
        ("", 0),
        (True, 1),                          # bool ialah int di Python
        (False, 0),
    ],
)
def test_coercion_table(nilai, jangkaan):
    pa = _plugin()
    assert pa._completed_at_sort_value(nilai) == jangkaan


def test_invalid_text_does_not_raise():
    # Ini teras tampalan: teks tidak sah mesti dikendalikan, bukan dibaling.
    pa = _plugin()
    assert pa._completed_at_sort_value("2026-09-24T20:46:00Z") == 0


# ---------------------------------------------------------------------------
# Tingkah laku susunan sebenar — inilah yang pecah sebelum tampalan
# ---------------------------------------------------------------------------


def _sorted_done(rows):
    """Tiru dua susunan bersimen yang dipakai ``get_board()`` untuk lajur done."""
    pa = _plugin()
    out = sorted(rows, key=lambda d: d["id"], reverse=True)
    out.sort(key=lambda d: (d["completed_at"] is None, -pa._completed_at_sort_value(d["completed_at"])))
    return [d["id"] for d in out]


def test_mixed_types_do_not_raise():
    # Tanpa tampalan: TypeError. Dengan tampalan: susunan selesai.
    ids = _sorted_done(
        [
            {"id": 1, "completed_at": 1_700_000_000},
            {"id": 2, "completed_at": "bukan cap masa"},   # baris lama rosak
            {"id": 3, "completed_at": None},               # belum selesai
            {"id": 4, "completed_at": "1699999999"},       # teks angka sah
        ]
    )
    assert sorted(ids) == [1, 2, 3, 4], "semua baris mesti tersusun tanpa baling"


def test_none_sorts_last_and_newest_first():
    ids = _sorted_done(
        [
            {"id": 1, "completed_at": 1_700_000_000},
            {"id": 2, "completed_at": None},
            {"id": 3, "completed_at": 1_699_999_999},
        ]
    )
    assert ids == [1, 3, 2], "completed_at DESC, NULL terakhir"


def test_unparseable_text_groups_with_the_oldest():
    # Teks tidak sah -> 0, jadi ia jatuh ke HUJUNG senarai bukan-NULL,
    # dan kekal stabil ikut id DESC.
    ids = _sorted_done(
        [
            {"id": 1, "completed_at": 1_700_000_000},
            {"id": 2, "completed_at": "rosak"},
            {"id": 3, "completed_at": 1_699_000_000},
        ]
    )
    assert ids == [1, 3, 2]


def test_numeric_string_orders_by_value_not_lexically():
    # Perangkap teks: susunan leksikal akan songsang '9...' lawan '1_00...' pada
    # panjang berbeza. Koersi int menjadikannya betul.
    ids = _sorted_done(
        [
            {"id": 1, "completed_at": "999999999"},     # lebih LAMA (9 digit)
            {"id": 2, "completed_at": "1700000000"},    # lebih BAHARU (10 digit)
        ]
    )
    assert ids == [2, 1], "10 digit (lebih baharu) mesti dahulu, bukan leksikal"
