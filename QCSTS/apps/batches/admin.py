from django.contrib import admin
from apps.batches.models import Batch


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = [
        "batch_number",
        "product",
        "study_type",
        "status",
        "incubation_date",
        "qty_remaining",
    ]
    list_filter = ["status", "study_type"]
    search_fields = ["batch_number", "product__name"]
    readonly_fields = ["created_at", "updated_at", "created_by", "qty_remaining"]
    ordering = ["-created_at"]
