"""text_stats.py 的 unittest 测试（仅使用 Python 标准库 unittest）。

运行方式（在 examples/dag_recovery_20261016 目录下）::

    python3 -m unittest discover -v
    python3 -m unittest test_text_stats -v
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import text_stats

SCRIPT = Path(__file__).resolve().with_name("text_stats.py")


class CountLinesTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(text_stats.count_lines(""), 0)

    def test_single_line_without_newline(self):
        self.assertEqual(text_stats.count_lines("hello"), 0)

    def test_single_newline_counts_one_line(self):
        self.assertEqual(text_stats.count_lines("hello\n"), 1)

    def test_multiple_lines(self):
        self.assertEqual(text_stats.count_lines("one\ntwo\nthree\n"), 3)

    def test_consecutive_newlines(self):
        self.assertEqual(text_stats.count_lines("a\n\nb"), 2)


class CountWordsTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(text_stats.count_words(""), 0)

    def test_only_whitespace(self):
        self.assertEqual(text_stats.count_words("  \n\t  "), 0)

    def test_single_word(self):
        self.assertEqual(text_stats.count_words("hello"), 1)

    def test_multiple_words_mixed_whitespace(self):
        self.assertEqual(text_stats.count_words("a  b\tc\nd"), 4)

    def test_punctuation_is_part_of_word(self):
        self.assertEqual(text_stats.count_words("don't, stop!"), 2)


class StatsTests(unittest.TestCase):
    def test_stats_tuple(self):
        self.assertEqual(text_stats.stats("one two\nthree\n"), (2, 3))

    def test_stats_agrees_with_components(self):
        text = "alpha beta\n\ngamma\n"
        self.assertEqual(
            text_stats.stats(text),
            (text_stats.count_lines(text), text_stats.count_words(text)),
        )


class CliTests(unittest.TestCase):
    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
        )

    def test_cli_counts_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "sample.txt"
            sample.write_text("one two\nthree\n", encoding="utf-8")
            proc = self._run(str(sample))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(proc.stdout.strip().split(), ["2", "3", str(sample)])

    def test_cli_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.txt"
            proc = self._run(str(missing))
            self.assertEqual(proc.returncode, 1)
            self.assertIn("无法读取", proc.stderr)

    def test_main_without_args_returns_2(self):
        self.assertEqual(text_stats.main([]), 2)

    def test_main_help_returns_0(self):
        self.assertEqual(text_stats.main(["--help"]), 0)


class IntegrationTests(unittest.TestCase):
    def test_real_file_via_stats_function(self):
        """通过真实文件读取路径验证统计结果。"""
        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "input.txt"
            sample.write_text(
                "The quick brown fox\njumps over the lazy dog\n", encoding="utf-8"
            )
            lines, words = text_stats.stats(sample.read_text(encoding="utf-8"))
            self.assertEqual(lines, 2)
            self.assertEqual(words, 9)


if __name__ == "__main__":
    unittest.main()