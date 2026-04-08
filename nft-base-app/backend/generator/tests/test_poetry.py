"""
tests/test_poetry.py – Unit tests for src/poetry.py
"""

from __future__ import annotations

import pytest

from src.poetry import FORMS, PoetryGenerator, _RHYME_GROUPS, generate_poem


# ---------------------------------------------------------------------------
# PoetryGenerator – structural tests
# ---------------------------------------------------------------------------


class TestHaiku:
    def test_has_three_lines(self):
        assert len(PoetryGenerator().haiku().splitlines()) == 3

    def test_lines_are_non_empty(self):
        for line in PoetryGenerator(seed=1).haiku().splitlines():
            assert line.strip()

    def test_first_line_capitalised(self):
        first = PoetryGenerator(seed=5).haiku().splitlines()[0]
        assert first[0].isupper()

    def test_seeded_output_is_deterministic(self):
        assert PoetryGenerator(seed=42).haiku() == PoetryGenerator(seed=42).haiku()

    def test_different_seeds_produce_variety(self):
        poems = {PoetryGenerator(seed=i).haiku() for i in range(20)}
        assert len(poems) > 1


class TestCouplet:
    def test_has_two_lines(self):
        assert len(PoetryGenerator().couplet().splitlines()) == 2

    def test_lines_are_non_empty(self):
        for line in PoetryGenerator(seed=2).couplet().splitlines():
            assert line.strip()

    def test_seeded_output_is_deterministic(self):
        assert PoetryGenerator(seed=99).couplet() == PoetryGenerator(seed=99).couplet()

    def test_end_words_rhyme(self):
        """The last word of each line must belong to the same rhyme group."""
        for seed in range(15):
            poem = PoetryGenerator(seed=seed).couplet()
            lines = poem.splitlines()
            assert len(lines) == 2
            # Strip trailing punctuation to isolate the last word
            end_words = [ln.rstrip(".,!?").split()[-1].lower() for ln in lines]
            rhymes = any(
                end_words[0] in grp and end_words[1] in grp
                for grp in _RHYME_GROUPS
            )
            assert rhymes, (
                f"Couplet lines don't rhyme at seed={seed}: {end_words!r}\n{poem}"
            )


class TestFreeVerse:
    def test_has_four_to_six_lines(self):
        for seed in range(10):
            n = len(PoetryGenerator(seed=seed).free_verse().splitlines())
            assert 4 <= n <= 6, f"Expected 4-6 lines, got {n} (seed={seed})"

    def test_lines_are_non_empty(self):
        for line in PoetryGenerator(seed=3).free_verse().splitlines():
            assert line.strip()

    def test_seeded_output_is_deterministic(self):
        assert (
            PoetryGenerator(seed=7).free_verse()
            == PoetryGenerator(seed=7).free_verse()
        )


class TestLimerick:
    def test_has_five_lines(self):
        assert len(PoetryGenerator().limerick().splitlines()) == 5

    def test_lines_are_non_empty(self):
        for line in PoetryGenerator(seed=4).limerick().splitlines():
            assert line.strip()

    def test_seeded_output_is_deterministic(self):
        assert (
            PoetryGenerator(seed=13).limerick()
            == PoetryGenerator(seed=13).limerick()
        )


# ---------------------------------------------------------------------------
# generate() dispatcher
# ---------------------------------------------------------------------------


class TestGenerate:
    def test_dispatches_all_named_forms(self):
        gen = PoetryGenerator(seed=0)
        for form in FORMS:
            result = gen.generate(form)
            assert isinstance(result, str)
            assert result.strip()

    def test_random_form_returns_a_poem(self):
        result = PoetryGenerator(seed=0).generate("random")
        assert isinstance(result, str)
        assert result.strip()

    def test_unknown_form_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown form"):
            PoetryGenerator().generate("sonnet")

    def test_generate_poem_convenience_function(self):
        result = generate_poem(form="haiku", seed=7)
        assert isinstance(result, str)
        assert len(result.splitlines()) == 3


# ---------------------------------------------------------------------------
# CLI – poem subcommand
# ---------------------------------------------------------------------------


class TestPoemSubcommand:
    def test_poem_subcommand_registered(self):
        from src.main import build_parser

        parser = build_parser()
        args = parser.parse_args(["poem", "--form", "haiku"])
        assert args.command == "poem"
        assert args.form == "haiku"

    def test_poem_defaults(self):
        from src.main import build_parser

        parser = build_parser()
        args = parser.parse_args(["poem"])
        assert args.form == "random"
        assert args.seed is None
        assert args.count == 1
        assert args.output is None

    def test_poem_seed_and_count(self):
        from src.main import build_parser

        parser = build_parser()
        args = parser.parse_args(["poem", "--seed", "42", "--count", "3"])
        assert args.seed == 42
        assert args.count == 3

    def test_cmd_poem_returns_zero(self, capsys):
        from argparse import Namespace

        from src.main import cmd_poem

        args = Namespace(form="haiku", seed=1, count=1, output=None)
        rc = cmd_poem(args)
        assert rc == 0
        captured = capsys.readouterr()
        assert captured.out.strip()

    def test_cmd_poem_multiple_count(self, capsys):
        from argparse import Namespace

        from src.main import cmd_poem

        args = Namespace(form="couplet", seed=10, count=3, output=None)
        rc = cmd_poem(args)
        assert rc == 0
        output = capsys.readouterr().out
        # Three poems separated by blank lines → at least two blank lines
        assert output.count("\n\n") >= 2

    def test_cmd_poem_writes_output_file(self, tmp_path, capsys):
        from argparse import Namespace

        from src.main import cmd_poem

        out_file = tmp_path / "poem.txt"
        args = Namespace(
            form="limerick", seed=5, count=1, output=str(out_file)
        )
        rc = cmd_poem(args)
        assert rc == 0
        assert out_file.is_file()
        content = out_file.read_text(encoding="utf-8")
        assert content.strip()
