import re
import logging

logger = logging.getLogger(__name__)


class OutcomeEvaluator:
    """
    Evaluates whether a test result passes or fails
    against its specification.

    Supported specification formats:
        - Range:     "98.0 - 102.0"  or  "98.0% - 102.0%"
        - NLT:       "NLT 75"        (Not Less Than)
        - NMT:       "NMT 5.0"       (Not More Than)
        - Exact:     "7.0"           (exact value with tolerance)

    Usage:
        result = OutcomeEvaluator.evaluate("99.5", "98.0 - 102.0")
        # returns "pass" or "fail"
    """

    @classmethod
    def evaluate(cls, value: str, specification: str) -> str:
        """
        Evaluates a value against a specification.

        Args:
            value: The measured value as a string e.g. "99.5"
            specification: The spec string e.g. "98.0 - 102.0"

        Returns:
            "pass" or "fail"
        """
        try:
            numeric_value = cls._extract_number(value)
            if numeric_value is None:
                logger.warning("Could not parse value: %s", value)
                return "fail"

            spec = specification.strip()

            # Range: "98.0 - 102.0" or "98.0% - 102.0%"
            range_match = re.match(r"(\d+\.?\d*)\s*%?\s*[-–]\s*(\d+\.?\d*)\s*%?", spec)
            if range_match:
                low = float(range_match.group(1))
                high = float(range_match.group(2))
                return "pass" if low <= numeric_value <= high else "fail"

            # NLT: Not Less Than
            nlt_match = re.match(r"NLT\s*(\d+\.?\d*)", spec, re.IGNORECASE)
            if nlt_match:
                threshold = float(nlt_match.group(1))
                return "pass" if numeric_value >= threshold else "fail"

            # NMT: Not More Than
            nmt_match = re.match(r"NMT\s*(\d+\.?\d*)", spec, re.IGNORECASE)
            if nmt_match:
                threshold = float(nmt_match.group(1))
                return "pass" if numeric_value <= threshold else "fail"

            # Exact value with 2% tolerance
            exact_match = re.match(r"^(\d+\.?\d*)$", spec)
            if exact_match:
                target = float(exact_match.group(1))
                tolerance = target * 0.02
                return "pass" if abs(numeric_value - target) <= tolerance else "fail"

            logger.warning("Unrecognized specification format: %s", spec)
            return "fail"

        except Exception as e:
            logger.error("OutcomeEvaluator error: %s", str(e))
            return "fail"

    @staticmethod
    def _extract_number(value: str):
        """Extracts the first numeric value from a string."""
        match = re.search(r"(\d+\.?\d*)", str(value))
        if match:
            return float(match.group(1))
        return None
