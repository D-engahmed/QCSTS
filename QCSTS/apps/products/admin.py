from django.contrib import admin
from apps.products.models import Monograph, MonographTest, Product


@admin.register(Monograph)
class MonographAdmin(admin.ModelAdmin):
    list_display = ["name", "version", "status", "effective_date", "approved_by"]
    list_filter = ["status"]
    search_fields = ["name", "version"]
    readonly_fields = ["approved_by", "approved_at", "created_at", "updated_at"]


@admin.register(MonographTest)
class MonographTestAdmin(admin.ModelAdmin):
    list_display = ["name", "monograph", "method", "specification", "sequence"]
    list_filter = ["monograph"]
    search_fields = ["name", "method"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "strength", "dosage_form", "monograph", "is_active"]
    list_filter = ["dosage_form", "is_active"]
    search_fields = ["name", "strength"]
