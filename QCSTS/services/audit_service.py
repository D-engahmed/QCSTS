import json
import logging
from django.core.serializers.json import DjangoJSONEncoder
from apps.audit.models import AuditLog
from core.exceptions import AuditLogFailure

logger = logging.getLogger(__name__)


def _json_safe(value):
    """Normalize audit payloads to JSON-native values before storing them in JSONField."""
    if value is None:
        return None
    return json.loads(json.dumps(value, cls=DjangoJSONEncoder))


class AuditService:
    """Single entry point for immutable audit records."""

    @staticmethod
    def log(performed_by, action, model_name, object_id, object_repr, old_value=None,
            new_value=None, ip_address=None, notes="", organization=None, required=True):
        try:
            AuditLog.objects.create(
                performed_by=performed_by,
                action=action,
                model_name=model_name,
                object_id=str(object_id),
                object_repr=str(object_repr),
                old_value=_json_safe(old_value),
                new_value=_json_safe(new_value),
                ip_address=ip_address,
                notes=notes,
                organization=organization,
            )
        except Exception as e:
            logger.error(
                "AuditService failed to write log | action=%s model=%s object=%s error=%s",
                action, model_name, object_id, str(e), exc_info=True,
            )
            if required:
                raise AuditLogFailure() from e
