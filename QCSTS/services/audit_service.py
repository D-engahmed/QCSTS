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
    - Audit persistence is fail-closed for security-critical operations.

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
        organization=None,
        required=True,
    ):
        """
        Creates an immutable audit log entry.

        Security-critical operations fail closed when audit persistence fails.
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
                organization=organization,  # NEW
            )
        except Exception as e:
            logger.error(
                "AuditService failed to write log | action=%s model=%s object=%s error=%s",
                action,
                model_name,
                object_id,
                str(e),
                exc_info=True,
            )
            if required:
                raise AuditLogFailure() from e