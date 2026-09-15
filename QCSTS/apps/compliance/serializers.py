from rest_framework import serializers
from .models import ElectronicSignature, ValidationArtifact


class ElectronicSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronicSignature
        fields = "__all__"
        read_only_fields = ("organization", "signer", "signed_at", "authentication_fingerprint", "signature_digest")


class ValidationArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationArtifact
        fields = "__all__"
        read_only_fields = ("organization",)
