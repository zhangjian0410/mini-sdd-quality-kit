"""Establish the paired fixture's ground truth outside the review execution."""

from pathlib import Path
import unittest


FIXTURES = Path(__file__).parent / "fixtures"


class FixtureOracleTests(unittest.TestCase):
    def function(self, variant):
        source = FIXTURES / variant / "pricing.py"
        namespace = {}
        exec(compile(source.read_text(), str(source), "exec"), namespace)
        return namespace["mean_price"]

    def test_known_defect_raises_for_a_nonempty_price_list(self):
        with self.assertRaises(TypeError):
            self.function("logic_bug")([10.0, 20.0])

    def test_corrected_fixture_returns_the_known_mean(self):
        self.assertEqual(self.function("corrected")([10.0, 20.0]), 15.0)

    def test_corrected_fixture_handles_an_empty_price_list(self):
        self.assertEqual(self.function("corrected")([]), 0.0)


if __name__ == "__main__":
    unittest.main()
