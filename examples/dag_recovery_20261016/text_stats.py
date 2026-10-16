"""text_stats.py — 文本统计器（仅使用 Python 标准库）。

统计文本或文本文件的行数与单词数。

统计口径：
- 行数（lines）：文本中换行符 ``\\n`` 的数量（与 ``wc -l`` 一致）。
- 单词数（words）：按任意空白字符切分后得到的非空片段数量。

命令行用法::

    python3 text_stats.py <文件>

输出格式: ``<行数> <单词数> <文件路径>``
"""

from __future__ import annotations

import sys
from pathlib import Path

__all__ = ["count_lines", "count_words", "stats", "main"]

USAGE = "用法: python3 text_stats.py <文件>\n输出: <行数> <单词数> <文件路径>"


def count_lines(text: str) -> int:
    """返回行数：文本中换行符的数量。"""
    return text.count("\n")


def count_words(text: str) -> int:
    """返回单词数：按空白切分后的非空片段数量。"""
    return len(text.split())


def stats(text: str) -> tuple[int, int]:
    """返回 (行数, 单词数) 二元组。"""
    return count_lines(text), count_words(text)


def main(argv: list[str] | None = None) -> int:
    """命令行入口：统计指定 UTF-8 文本文件的行数与单词数。

    返回进程退出码：0 成功；1 读取失败；2 参数缺失。
    """
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print(USAGE, file=sys.stderr)
        return 2
    if args[0] in ("-h", "--help"):
        print(USAGE)
        return 0

    path = Path(args[0])
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"text_stats: 无法读取 {path}: {exc}", file=sys.stderr)
        return 1

    lines, words = stats(text)
    print(f"{lines} {words} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())