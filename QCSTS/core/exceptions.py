from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


# ===================== Base Exception =====================
class QCSTSException(Exception):
    """
    Base class for all QCSTS business exceptions.
    Every custom exception inherits from this so we can
    catch all business errors in one place in the global handler.
    """

    default_message = "An unexpected error occurred."
    default_status = status.HTTP_400_BAD_REQUEST

    def __init__(self, message=None, status_code=None):
        self.message = message or self.default_message
        self.status_code = status_code or self.default_status
        super().__init__(self.message)


# ===================== Authentication & Signature Exceptions =====================


class SignatureFailedError(QCSTSException):
    """
    Raised when an electronic signature verification fails.
    This means the analyst entered the wrong password when
    trying to sign a test result submission.
    """

    default_message = "Signature verification failed. Please re-enter your password."
    default_status = status.HTTP_401_UNAUTHORIZED


class AccountLockedError(QCSTSException):
    """
    Raised when a user account is locked due to
    too many failed login or signature attempts.
    """

    default_message = "Account is locked. Please contact your administrator."
    default_status = status.HTTP_403_FORBIDDEN


class SignatureTokenExpiredError(QCSTSException):
    """
    Raised when the SignatureToken from Redis has expired
    (TTL = 5 minutes). The analyst must re-sign.
    """

    default_message = "Signature session expired. Please verify your identity again."
    default_status = status.HTTP_401_UNAUTHORIZED


# ===================== Monograph & Product Exceptions =====================
class MonographNotApproved(QCSTSException):
    """
    Raised when someone tries to create a Batch for a Product
    that does not have an approved Monograph assigned.
    Rule R-01 from our business rules.
    """

    default_message = "Cannot create a batch. The product does not have an approved monograph."
    default_status = status.HTTP_422_UNPROCESSABLE_ENTITY


class MonographAlreadyApproved(QCSTSException):
    """
    Raised when someone tries to approve a monograph
    that is already in approved state.
    """

    default_message = "This monograph is already approved."
    default_status = status.HTTP_409_CONFLICT


# ===================== Batch & Schedule Exceptions =====================


class DuplicateBatchNumber(QCSTSException):
    """
    Raised when a batch_number already exists in the system.
    Batch numbers must be globally unique.
    """

    default_message = "A batch with this number already exists."
    default_status = status.HTTP_409_CONFLICT


class ScheduleGenerationError(QCSTSException):
    """
    Raised when the ScheduleEngine fails to generate test points.
    This should be extremely rare — it indicates a data problem
    with the batch (e.g., invalid incubation date).
    """

    default_message = "Failed to generate stability test schedule. Check batch dates."
    default_status = status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPointNotEditable(QCSTSException):
    """
    Raised when someone tries to create or delete a TestPoint
    directly via the API. Test points are only created by
    ScheduleEngine and never manually. Rule R-02.
    """

    default_message = "Test points cannot be created or deleted manually."
    default_status = status.HTTP_403_FORBIDDEN


# ===================== Result & Chamber Exceptions =====================


class ResultAlreadySubmitted(QCSTSException):
    """
    Raised when an analyst tries to submit a result for a
    (test_point, monograph_test) pair that already has a result.
    Prevents duplicate entries.
    """

    default_message = "A result for this test has already been submitted."
    default_status = status.HTTP_409_CONFLICT


class InsufficientQuantity(QCSTSException):
    """
    Raised when a sample pull request exceeds qty_remaining
    for a batch in the chamber.
    """

    default_message = "Insufficient quantity remaining in chamber for this pull."
    default_status = status.HTTP_422_UNPROCESSABLE_ENTITY


class InvalidStudyType(QCSTSException):
    """
    Raised when an unknown study type is passed to ScheduleEngine.
    Valid types are: long_term, accelerated, intermediate.
    """

    default_message = "Invalid study type. Must be long_term, accelerated, or intermediate."
    default_status = status.HTTP_400_BAD_REQUEST


# =====================  Audit Exception (non-fatal) =====================
class AuditLogFailure(QCSTSException):
    """
    Raised internally when AuditService fails to write a log entry.
    This is NON-FATAL — it must never block the primary operation.
    AuditService catches this and writes to a local file instead.
    """

    default_message = "Audit log could not be written."
    default_status = status.HTTP_500_INTERNAL_SERVER_ERROR


# ===================== Global DRF Exception Handler =====================


def qcsts_exception_handler(exc, context):
    """
    Global exception handler registered in Django settings under:
    REST_FRAMEWORK = { 'EXCEPTION_HANDLER': 'core.exceptions.qcsts_exception_handler' }

    How it works:
    1. First let DRF handle its own exceptions (ValidationError, NotAuthenticated, etc.)
    2. Then catch our custom QCSTSException subclasses
    3. Finally catch any unexpected Exception and return a safe 500

    The client ALWAYS gets our standard envelope. Never a raw Django traceback.
    """

    # Step 1: Let DRF handle its own exceptions first
    response = exception_handler(exc, context)

    if response is not None:
        # DRF handled it — reformat into our envelope
        return Response(
            {
                "success": False,
                "data": None,
                "errors": response.data,
            },
            status=response.status_code,
        )

    # Step 2: Handle our custom business exceptions
    if isinstance(exc, QCSTSException):
        logger.warning("Business exception: %s | %s", exc.__class__.__name__, exc.message)
        return Response(
            {
                "success": False,
                "data": None,
                "errors": {"non_field_errors": [exc.message]},
            },
            status=exc.status_code,
        )

    # Step 3: Catch anything else — log it, return safe 500
    logger.error(
        "Unhandled exception in %s: %s",
        context.get("view").__class__.__name__ if context.get("view") else "unknown",
        str(exc),
        exc_info=True,  # includes full traceback in logs
    )
    return Response(
        {
            "success": False,
            "data": None,
            "errors": {"non_field_errors": ["An internal server error occurred."]},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
