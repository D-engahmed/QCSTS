from django.contrib import admin
from apps.chamber.models import SamplePull, LocationHistory


@admin.register(SamplePull)
class SamplePullAdmin(admin.ModelAdmin):
    list_display = ["batch", "qty_pulled", "pulled_by", "pulled_at"]
    list_filter = ["pulled_at"]
    search_fields = ["batch__batch_number"]
    readonly_fields = ["pulled_at", "pulled_by", "created_at"]


@admin.register(LocationHistory)
class LocationHistoryAdmin(admin.ModelAdmin):
    list_display = ["batch", "old_shelf", "new_shelf", "changed_by", "created_at"]
    search_fields = ["batch__batch_number"]
    readonly_fields = ["created_at", "changed_by"]
