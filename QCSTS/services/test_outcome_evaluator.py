from django.test import SimpleTestCase

from services.outcome_evaluator import OutcomeEvaluator


class OutcomeEvaluatorTests(SimpleTestCase):
    def test_nlt_uses_specification_precision(self):
        self.assertEqual(OutcomeEvaluator.evaluate("74.96", "NLT 75"), "pass")

    def test_nmt_uses_specification_precision(self):
        self.assertEqual(OutcomeEvaluator.evaluate("5.04", "NMT 5.0"), "fail")
        self.assertEqual(OutcomeEvaluator.evaluate("5.04", "NMT 5"), "fail")

    def test_range_uses_declared_precision(self):
        self.assertEqual(OutcomeEvaluator.evaluate("97.96", "98.0 - 102.0"), "pass")
        self.assertEqual(OutcomeEvaluator.evaluate("97.94", "98.0 - 102.0"), "fail")

    def test_decimal_comparison_does_not_use_binary_float(self):
        self.assertEqual(OutcomeEvaluator.evaluate("0.30", "0.3"), "pass")
