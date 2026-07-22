from rest_framework import serializers
from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for displaying audit log entries.
    No create/update operations — audit logs are written
    exclusively by AuditService, never through the API.
    """

    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "performed_by",
            "performed_by_name",
            "action",
            "model_name",
            "object_id",
            "object_repr",
            "old_value",
            "new_value",
            "ip_address",
            "timestamp",
            "notes",
        ]
        read_only_fields = fields

    def get_performed_by_name(self, obj):
        if obj.performed_by:
            return obj.performed_by.full_name
        return "System"
