#!/usr/bin/env python3
"""csv_totals.py — 按类别汇总 CSV 中的金额（Decimal 精确运算，支持负数）。

仅使用 Python 标准库。

输入 CSV 需包含名为 category 和 amount 的表头列（顺序不限）；
amount 使用 decimal.Decimal 解析，运算精确，支持负数。
输出为一行一条 "category,total" 记录，total 保留 Decimal 字符串形式。

用法:
    python3 csv_totals.py data.csv
    cat data.csv | python3 csv_totals.py
"""

import argparse
import csv
import sys
from decimal import Decimal


def totals_from_csv(fileobj):
    """从 CSV 文件对象读取 category/amount 两列，返回 {category: Decimal} 汇总。

    忽略完全空白的行；金额用 Decimal 精确累加，负数同样支持。
    表头缺少 category 或 amount 列时抛出 ValueError。
    """
    reader = csv.DictReader(fileobj)
    fieldnames = reader.fieldnames
    if fieldnames is None:
        raise ValueError("CSV 为空：缺少表头行")

    normalized = [h.strip().lower() for h in fieldnames]
    try:
        cat_index = normalized.index("category")
        amt_index = normalized.index("amount")
    except ValueError as exc:
        raise ValueError("CSV 表头必须包含 category 与 amount 列") from exc

    totals = {}
    for row in reader:
        cat = row[fieldnames[cat_index]]
        raw = row[fieldnames[amt_index]]
        if cat is None and raw is None:
            continue  # 纯空行
        if cat is None or not cat.strip():
            raise ValueError("存在空的 category 值")
        if raw is None or not raw.strip():
            raise ValueError(f"类别 {cat.strip()!r} 存在空的 amount 值")
        category = cat.strip()
        totals[category] = totals.get(category, Decimal("0")) + Decimal(raw.strip())
    return totals


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="按类别汇总 CSV 中的 Decimal 金额（支持负数）"
    )
    parser.add_argument(
        "csv_file",
        nargs="?",
        help="CSV 文件路径；缺省时从标准输入读取",
    )
    args = parser.parse_args(argv)

    try:
        if args.csv_file:
            with open(args.csv_file, newline="", encoding="utf-8") as fh:
                totals = totals_from_csv(fh)
        else:
            totals = totals_from_csv(sys.stdin)
    except (ValueError, OSError) as exc:
        print(f"csv_totals: 错误: {exc}", file=sys.stderr)
        return 2

    for category, total in totals.items():
        print(f"{category},{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())