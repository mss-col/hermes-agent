"""Shared GFM table → bullet conversion helpers."""

from gateway.platforms.helpers import (
    TABLE_SEPARATOR_RE,
    is_table_row,
    split_markdown_table_row,
    convert_table_to_bullets,
)


class TestTablePrimitives:

    def test_separator_re_matches_basic(self):
        assert TABLE_SEPARATOR_RE.match("|---|---|")


    def test_is_table_row_with_pipe(self):
        assert is_table_row("| Alice | 150 |")


class TestConvertTableToBullets:

    def test_basic_table(self):
        text = (
            "| Player | Score |\n"
            "|--------|-------|\n"
            "| Alice  | 150   |\n"
            "| Bob    | 120   |"
        )
        out = convert_table_to_bullets(text)
        assert "**Alice**" in out
        assert "• Score: 150" in out
        assert "**Bob**" in out
        assert "• Score: 120" in out
        assert "• Player: Alice" not in out

    def test_three_column_table(self):
        text = (
            "| Name | Age | City |\n"
            "|:-----|----:|:----:|\n"
            "| Ada  |  30 | NYC  |"
        )
        out = convert_table_to_bullets(text)
        assert "**Ada**" in out
        assert "• Name: Ada" not in out
        assert "• Age: 30" in out
        assert "• City: NYC" in out
        assert "**Ada**\n• Age: 30\n• City: NYC" in out

    def test_row_label_column(self):
        text = (
            "|        | Score | Rank |\n"
            "|--------|-------|------|\n"
            "| Alice  | 150   | 1    |\n"
            "| Bob    | 120   | 2    |"
        )
        out = convert_table_to_bullets(text)
        assert "**Alice**" in out
        assert "• Score: 150" in out
        assert "• Rank: 1" in out
        assert "**Alice**\n• Score: 150\n• Rank: 1" in out

    def test_bare_pipe_table(self):
        text = "head1 | head2\n--- | ---\na | b\nc | d"
        out = convert_table_to_bullets(text)
        assert "**a**" in out
        assert "• head1: a" not in out
        assert "• head2: b" in out

    def test_heading_already_bold_no_double_star(self):
        # Regression: a heading cell written as **X** must not be wrapped
        # again into ****X**** (4 asterisks) — Telegram renders that as bold
        # "X" plus a literal "**".
        text = (
            "| h1 | h2 |\n"
            "|---|---|\n"
            "| **Alice** | 150 |"
        )
        out = convert_table_to_bullets(text)
        assert "****" not in out
        assert "**Alice**" in out
        assert "• h2: 150" in out

    def test_heading_bold_with_trailing_text_no_double_star(self):
        # Regression: **X** (trailing text) starts with ** but does not end
        # with **. The first fix only guarded fully-bold headings, so this
        # case was still wrapped again -> ****X** (text)**. Must stay clean.
        text = (
            "| Ujian | Status |\n"
            "|---|---|\n"
            "| **typecheck** (patch preflight) | LULUS |"
        )
        out = convert_table_to_bullets(text)
        assert "****" not in out
        assert "**typecheck (patch preflight)**" in out
        assert "• Status: LULUS" in out

    def test_heading_unbalanced_bold_marker(self):
        # Regression: an unbalanced "**Alice" must not leak a literal "**".
        # Normalizing strips the marker and re-wraps once -> "**Alice**".
        text = (
            "| h1 | h2 |\n"
            "|---|---|\n"
            "| **Alice | 150 |"
        )
        out = convert_table_to_bullets(text)
        assert "****" not in out
        assert "**Alice**" in out
        assert "• h2: 150" in out

    def test_heading_partial_bold_normalized(self):
        # A heading with bold in the middle ("Cost **high** risk") is
        # normalized to a single fully-bold label, never double-wrapped.
        text = (
            "| h1 | h2 |\n"
            "|---|---|\n"
            "| Cost **high** risk | 150 |"
        )
        out = convert_table_to_bullets(text)
        assert "****" not in out
        assert "**Cost high risk**" in out
        assert "• h2: 150" in out


