from django.contrib import admin
from apps.results.models import TestResult


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ["monograph_test", "test_point", "value", "pass_fail", "analyst", "submitted_at"]
    list_filter = ["pass_fail"]
    search_fields = ["monograph_test__name", "test_point__batch__batch_number"]
    readonly_fields = [
        "id",
        "test_point",
        "monograph_test",
        "value",
        "specification_snapshot",
        "pass_fail",
        "analyst",
        "submitted_at",
        "created_at",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
