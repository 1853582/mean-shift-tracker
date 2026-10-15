"""Git/Pod 协作链路验收探针：is_even 及正反例 unittest。"""

import unittest


def is_even(value):
    """Return True if value is even, False otherwise."""
    return value % 2 == 0


class IsEvenTest(unittest.TestCase):
    def test_even_values_are_even(self):
        # 正例：偶数应判定为 True
        for value in (0, 2, 4, 100, -6):
            with self.subTest(value=value):
                self.assertTrue(is_even(value), f"{value} should be even")

    def test_odd_values_are_not_even(self):
        # 反例：奇数应判定为 False
        for value in (1, 3, 7, 101, -5):
            with self.subTest(value=value):
                self.assertFalse(is_even(value), f"{value} should be odd")


if __name__ == "__main__":
    unittest.main()
