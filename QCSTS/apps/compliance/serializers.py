from rest_framework import serializers
from .models import ControlledRecord, ElectronicSignature, ValidationArtifact


class ElectronicSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronicSignature
        fields = "__all__"
        read_only_fields = ("organization", "signer", "signed_at", "authentication_fingerprint", "signature_digest")


class ControlledRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ControlledRecord
        fields = "__all__"
        read_only_fields = ("organization", "locked_at", "locked_by", "approved_at", "approved_by")


class ValidationArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationArtifact
        fields = "__all__"
        read_only_fields = ("organization",)
