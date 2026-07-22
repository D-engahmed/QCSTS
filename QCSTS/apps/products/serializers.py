from rest_framework import serializers
from apps.products.models import Monograph, MonographTest, Product
from core.exceptions import MonographAlreadyApproved


class MonographTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonographTest
        fields = ["id", "name", "method", "specification", "unit", "sequence"]
        read_only_fields = ["id"]


class MonographSerializer(serializers.ModelSerializer):
    tests = MonographTestSerializer(many=True, read_only=True)
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Monograph
        fields = [
            "id",
            "name",
            "version",
            "effective_date",
            "status",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "tests",
            "created_at",
        ]
        read_only_fields = ["id", "approved_by", "approved_at", "created_at"]

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.full_name
        return None


class MonographCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monograph
        fields = ["name", "version", "effective_date", "status"]


class ProductSerializer(serializers.ModelSerializer):
    monograph_name = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "strength",
            "dosage_form",
            "description",
            "monograph",
            "monograph_name",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_monograph_name(self, obj):
        if obj.monograph:
            return str(obj.monograph)
        return None
