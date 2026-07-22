from rest_framework import serializers
from apps.accounts.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "email", "full_name", "role", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)

    class Meta:
        model = CustomUser
        fields = ["email", "full_name", "role", "password"]

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)