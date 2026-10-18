from plugins.platforms.slack.adapter import _align_table, _split_table_row, _wrap_markdown_tables

_ROW = r"| B10 | `git add -A \|\| true` telan ralat | `git add` per-fail |"


def test_split_table_row_keeps_escaped_pipes_inside_the_cell():
    assert _split_table_row(_ROW) == [
        "B10", r"`git add -A \|\| true` telan ralat", "`git add` per-fail"]


def test_align_table_does_not_invent_phantom_columns():
    out = _align_table(["| Kod | Penemuan | Pembetulan |", "|---|---|---|", _ROW])
    assert {len(_split_table_row(r)) for r in out} == {3}
    assert r"`git add -A \|\| true` telan ralat" in out[2]


def test_wrap_markdown_tables_end_to_end():
    out = _wrap_markdown_tables("| Kod | Penemuan | Pembetulan |\n|---|---|---|\n" + _ROW)
    body = [ln for ln in out.split("\n") if ln.startswith("|")]
    assert out.count("```") == 2
    assert {len(_split_table_row(ln)) for ln in body} == {3}
