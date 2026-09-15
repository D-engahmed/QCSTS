from rest_framework import serializers
from .models import CAPA, ChangeControl, Deviation, OOSInvestigation, OOTInvestigation


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        fields = "__all__"
        read_only_fields = ("organization",)


class OOSInvestigationSerializer(TenantSerializer):
    class Meta(TenantSerializer.Meta):
        model = OOSInvestigation


class OOTInvestigationSerializer(TenantSerializer):
    class Meta(TenantSerializer.Meta):
        model = OOTInvestigation


class DeviationSerializer(TenantSerializer):
    class Meta(TenantSerializer.Meta):
        model = Deviation


class CAPASerializer(TenantSerializer):
    class Meta(TenantSerializer.Meta):
        model = CAPA


class ChangeControlSerializer(TenantSerializer):
    class Meta(TenantSerializer.Meta):
        model = ChangeControl
