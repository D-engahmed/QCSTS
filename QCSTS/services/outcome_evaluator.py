import re
import math
import logging
from core.exceptions import EvaluationError

logger = logging.getLogger(__name__)

class OutcomeEvaluator:
    """
    Evaluates whether a test result passes or fails against its specification.

    Supported specification formats:
        - Range:     "98.0 - 102.0"  or  "98.0% - 102.0%"
        - NLT:       "NLT 75"        (Not Less Than)
        - NMT:       "NMT 5.0"       (Not More Than)
        - Exact:     "7.0"           (Strict equality using math.isclose)
    """

    @classmethod
    def evaluate(cls, value: str, specification: str) -> str:
        try:
            numeric_value = cls._extract_number(value)
            
            spec = specification.strip()

            # Range: "98.0 - 102.0" or "98.0% - 102.0%"
            range_match = re.match(r"^(-?\d+\.?\d*)\s*%?\s*[-–]\s*(-?\d+\.?\d*)\s*%?$", spec)
            if range_match:
                low = float(range_match.group(1))
                high = float(range_match.group(2))
                if low > high:
                    raise EvaluationError(f"Invalid range specification: {spec} (low > high)")
                return "pass" if low <= numeric_value <= high else "fail"

            # NLT: Not Less Than
            nlt_match = re.match(r"^NLT\s*(-?\d+\.?\d*)\s*%?$", spec, re.IGNORECASE)
            if nlt_match:
                threshold = float(nlt_match.group(1))
                return "pass" if numeric_value >= threshold else "fail"

            # NMT: Not More Than
            nmt_match = re.match(r"^NMT\s*(-?\d+\.?\d*)\s*%?$", spec, re.IGNORECASE)
            if nmt_match:
                threshold = float(nmt_match.group(1))
                return "pass" if numeric_value <= threshold else "fail"

            # Exact value (Strict Equality)
            exact_match = re.match(r"^(-?\d+\.?\d*)\s*%?$", spec)
            if exact_match:
                target = float(exact_match.group(1))
                # Use math.isclose for safe floating-point comparison
                return "pass" if math.isclose(numeric_value, target, rel_tol=1e-9) else "fail"

            # If no regex matched, the specification format is invalid
            raise EvaluationError(f"Unrecognized specification format: {spec}")

        except EvaluationError:
            raise
        except Exception as e:
            logger.error("OutcomeEvaluator unexpected error: %s", str(e))
            raise EvaluationError(f"Evaluation failed: {str(e)}")

    @staticmethod
    def _extract_number(value: str) -> float:
        """
        Strictly extracts a numeric value from a string.
        Supports negative numbers and rejects malformed inputs like '99.5.2'.
        """
        if value is None:
            raise EvaluationError("Value cannot be empty.")
            
        # Strict regex: optional negative sign, digits, optional decimal, optional %
        match = re.match(r"^\s*(-?\d+\.?\d*)\s*%?\s*$", str(value))
        if not match:
            raise EvaluationError(f"Cannot parse numeric value from: {value}")
            
        return float(match.group(1))