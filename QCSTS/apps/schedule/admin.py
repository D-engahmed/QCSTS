from django.contrib import admin
from apps.schedule.models import TestPoint


@admin.register(TestPoint)
class TestPointAdmin(admin.ModelAdmin):
    list_display = ["batch", "month", "scheduled_date", "status"]
    list_filter = ["status"]
    search_fields = ["batch__batch_number"]
    ordering = ["scheduled_date"]
    readonly_fields = ["batch", "month", "scheduled_date", "status", "completed_at", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
