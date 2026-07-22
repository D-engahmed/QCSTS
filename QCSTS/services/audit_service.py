import logging
from apps.audit.models import AuditLog
from core.exceptions import AuditLogFailure

logger = logging.getLogger(__name__)


class AuditService:
    """
    Single entry point for writing audit log records.

    Rules:
    - Called by every service that modifies data
    - Never called directly from views
    - If audit writing fails, it logs to file but never
      blocks the primary operation (non-fatal)

    Usage:
        AuditService.log(
            performed_by=request.user,
            action="UPDATE",
            model_name="Batch",
            object_id=str(batch.id),
            object_repr=str(batch),
            old_value={"status": "active"},
            new_value={"status": "inactive"},
            ip_address=request.META.get("REMOTE_ADDR"),
        )
    """

    @staticmethod
    def log(
        performed_by,
        action,
        model_name,
        object_id,
        object_repr,
        old_value=None,
        new_value=None,
        ip_address=None,
        notes="",
    ):
        """
        Creates an immutable audit log entry.

        If writing fails for any reason, the error is logged
        to file and the exception is swallowed — the primary
        operation must never fail because of an audit issue.
        """
        try:
            AuditLog.objects.create(
                performed_by=performed_by,
                action=action,
                model_name=model_name,
                object_id=str(object_id),
                object_repr=object_repr,
                old_value=old_value,
                new_value=new_value,
                ip_address=ip_address,
                notes=notes,
            )
        except Exception as e:
            # Non-fatal — log to file, never raise
            logger.error(
                "AuditService failed to write log | action=%s model=%s object=%s error=%s",
                action,
                model_name,
                object_id,
                str(e),
            )
