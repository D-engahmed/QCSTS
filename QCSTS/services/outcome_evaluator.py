import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import logging
from core.exceptions import EvaluationError

logger = logging.getLogger(__name__)

_NUMBER_RE = re.compile(r"^\s*(-?\d+(?:\.\d*)?)\s*%?\s*$")
_RANGE_RE = re.compile(r"^(-?\d+(?:\.\d*)?)\s*%?\s*[-–]\s*(-?\d+(?:\.\d*)?)\s*%?$")


class OutcomeEvaluator:
    """
    Evaluate a laboratory result against a controlled numeric specification.

    Numeric comparison deliberately uses Decimal rather than float. The value
    is rounded to the precision expressed by the specification before the
    comparison. This mirrors pharmacopeial reporting practice for specifications
    such as ``NLT 75``: a reported 74.96 is rounded to 75 and therefore passes.

    Supported formats:
        - Range: "98.0 - 102.0" or "98.0% - 102.0%"
        - NLT:   "NLT 75"
        - NMT:   "NMT 5.0"
        - Exact: "7.0"
    """

    @classmethod
    def evaluate(cls, value: str, specification: str) -> str:
        try:
            numeric_value = cls._extract_decimal(value)
            spec = specification.strip()

            range_match = _RANGE_RE.match(spec)
            if range_match:
                low = Decimal(range_match.group(1))
                high = Decimal(range_match.group(2))
                if low > high:
                    raise EvaluationError(f"Invalid range specification: {spec} (low > high)")
                precision = max(cls._decimal_places(range_match.group(1)), cls._decimal_places(range_match.group(2)))
                reported = cls._round_to_precision(numeric_value, precision)
                return "pass" if low <= reported <= high else "fail"

            nlt_match = re.match(r"^NLT\s*(-?\d+(?:\.\d*)?)\s*%?$", spec, re.IGNORECASE)
            if nlt_match:
                threshold = Decimal(nlt_match.group(1))
                reported = cls._round_to_precision(
                    numeric_value, cls._decimal_places(nlt_match.group(1))
                )
                return "pass" if reported >= threshold else "fail"

            nmt_match = re.match(r"^NMT\s*(-?\d+(?:\.\d*)?)\s*%?$", spec, re.IGNORECASE)
            if nmt_match:
                threshold = Decimal(nmt_match.group(1))
                reported = cls._round_to_precision(
                    numeric_value, cls._decimal_places(nmt_match.group(1))
                )
                return "pass" if reported <= threshold else "fail"

            exact_match = _NUMBER_RE.match(spec)
            if exact_match:
                target = Decimal(exact_match.group(1))
                reported = cls._round_to_precision(
                    numeric_value, cls._decimal_places(exact_match.group(1))
                )
                return "pass" if reported == target else "fail"

            raise EvaluationError(f"Unrecognized specification format: {spec}")

        except EvaluationError:
            raise
        except (InvalidOperation, ValueError) as exc:
            logger.error("OutcomeEvaluator numeric error: %s", exc)
            raise EvaluationError(f"Evaluation failed: {exc}") from exc
        except Exception as exc:
            logger.error("OutcomeEvaluator unexpected error: %s", exc)
            raise EvaluationError(f"Evaluation failed: {exc}") from exc

    @staticmethod
    def _extract_decimal(value: str) -> Decimal:
        if value is None:
            raise EvaluationError("Value cannot be empty.")
        match = _NUMBER_RE.match(str(value))
        if not match:
            raise EvaluationError(f"Cannot parse numeric value from: {value}")
        try:
            return Decimal(match.group(1))
        except InvalidOperation as exc:
            raise EvaluationError(f"Cannot parse numeric value from: {value}") from exc

    @staticmethod
    def _decimal_places(number: str) -> int:
        return max(0, -Decimal(number).as_tuple().exponent)

    @staticmethod
    def _round_to_precision(value: Decimal, decimal_places: int) -> Decimal:
        quantum = Decimal("1") if decimal_places == 0 else Decimal("1").scaleb(-decimal_places)
        return value.quantize(quantum, rounding=ROUND_HALF_UP)
