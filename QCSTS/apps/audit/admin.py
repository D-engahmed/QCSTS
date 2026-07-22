from django.contrib import admin
from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "model_name", "object_repr", "performed_by", "timestamp"]
    list_filter = ["action", "model_name"]
    search_fields = ["object_repr", "object_id"]
    ordering = ["-timestamp"]
    readonly_fields = [
        "id",
        "performed_by",
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

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
