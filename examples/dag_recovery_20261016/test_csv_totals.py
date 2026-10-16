#!/usr/bin/env python3
"""csv_totals.py 的 unittest 测试（仅标准库）。"""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from csv_totals import totals_from_csv

SCRIPT_PATH = Path(__file__).resolve().with_name("csv_totals.py")


class TotalsFromCsvTest(unittest.TestCase):
    """totals_from_csv 核心逻辑测试。"""

    def test_decimal_precision_0_10_plus_0_20_equals_0_30(self):
        """Decimal 精确运算：0.10 + 0.20 必须严格等于 0.30。"""
        data = "category,amount\na,0.10\na,0.20\n"
        totals = totals_from_csv(io.StringIO(data))
        self.assertEqual(totals["a"], Decimal("0.30"))
        self.assertEqual(str(totals["a"]), "0.30")

    def test_sum_by_category(self):
        data = "category,amount\nfood,10.50\nfood,2.25\ntoys,5.00\n"
        totals = totals_from_csv(io.StringIO(data))
        self.assertEqual(totals["food"], Decimal("12.75"))
        self.assertEqual(totals["toys"], Decimal("5.00"))

    def test_negative_amounts(self):
        """负数金额必须正确参与汇总（例如退款场景）。"""
        data = "category,amount\nfood,-10.50\nfood,3.00\nrefund,-1.25\nrefund,-4.75\n"
        totals = totals_from_csv(io.StringIO(data))
        self.assertEqual(totals["food"], Decimal("-7.50"))
        self.assertEqual(totals["refund"], Decimal("-6.00"))

    def test_mixed_positive_and_negative(self):
        data = "category,amount\nnet,100.00\nnet,-25.50\nnet,0.50\n"
        totals = totals_from_csv(io.StringIO(data))
        self.assertEqual(totals["net"], Decimal("75.00"))

    def test_columns_in_any_order(self):
        data = "amount,category\n1.10,food\n0.40,toys\n"
        totals = totals_from_csv(io.StringIO(data))
        self.assertEqual(totals["food"], Decimal("1.10"))
        self.assertEqual(totals["toys"], Decimal("0.40"))

    def test_blank_rows_skipped(self):
        data = "category,amount\nfood,1.00\n\nfood,2.00\n"
        totals = totals_from_csv(io.StringIO(data))
        self.assertEqual(totals["food"], Decimal("3.00"))

    def test_empty_input_raises(self):
        with self.assertRaises(ValueError):
            totals_from_csv(io.StringIO(""))

    def test_missing_header_raises(self):
        with self.assertRaises(ValueError):
            totals_from_csv(io.StringIO("foo,bar\n1,2\n"))


class CsvTotalsCliTest(unittest.TestCase):
    """CLI 入口（真实执行路径）冒烟测试。"""

    def test_cli_sums_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "sample.csv")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("category,amount\nfood,0.10\nfood,0.20\ntoy,5\n")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), path],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            lines = sorted(proc.stdout.strip().splitlines())
            self.assertEqual(lines, ["food,0.30", "toy,5"])

    def test_cli_reads_stdin(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            input="category,amount\nrefund,-1.25\nrefund,-4.75\n",
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "refund,-6.00")


if __name__ == "__main__":
    unittest.main()