from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import status

from apps.accounts.models import CustomUser
from apps.accounts.serializers import (
    LoginSerializer,
    UserSerializer,
    CreateUserSerializer,
    ChangePasswordSerializer,
)
from core.responses import success_response, error_response
from core.permissions import IsAdmin
from core.exceptions import AccountLockedError


class LoginView(APIView):
    serializer_class = LoginSerializer

    """
    POST /api/v1/auth/login/
    Accepts email + password, returns JWT tokens + user object.
    No authentication required — this is the entry point.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Store last login IP
        ip = request.META.get("REMOTE_ADDR")
        user.last_login_ip = ip
        user.save(update_fields=["last_login_ip"])

        return success_response(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            },
            status_code=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    serializer_class = LoginSerializer

    """
    POST /api/v1/auth/logout/
    Blacklists the refresh token so it cannot be reused.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            pass  # already blacklisted or invalid — still return 200
        return success_response(message="Logged out successfully.")


class MeView(APIView):
    serializer_class = UserSerializer

    """
    GET /api/v1/auth/me/
    Returns the currently logged-in user's profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(data=UserSerializer(request.user).data)


class UserListCreateView(APIView):
    permission_classes = [IsAdmin]
    def get(self, request):
        users = CustomUser.objects.all()
        return success_response(data=UserSerializer(users, many=True).data)

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(data=UserSerializer(user).data, status_code=status.HTTP_201_CREATED)

class UserDetailView(APIView):
    permission_classes = [IsAdmin]
    def get_object(self, pk):
        try: return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist: return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user: return error_response({"detail": "User not found."}, status.HTTP_404_NOT_FOUND)
        return success_response(data=UserSerializer(user).data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user: return error_response({"detail": "User not found."}, status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=UserSerializer(user).data)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user: return error_response({"detail": "User not found."}, status.HTTP_404_NOT_FOUND)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return success_response(message="User deactivated successfully.")

class UserDetailView(APIView):
    serializer_class = UserSerializer

    """
    GET    /api/v1/auth/users/<id>/  — get user detail (admin only)
    PATCH  /api/v1/auth/users/<id>/  — update user (admin only)
    DELETE /api/v1/auth/users/<id>/  — deactivate user (admin only)
    """

    permission_classes = [IsAdmin]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            return None

    def get(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return error_response({"detail": "User not found."}, status.HTTP_404_NOT_FOUND)
        return success_response(data=UserSerializer(user).data)

    def patch(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return error_response({"detail": "User not found."}, status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=UserSerializer(user).data)

    def delete(self, request, pk):
        user = self.get_object(pk)
        if not user:
            return error_response({"detail": "User not found."}, status.HTTP_404_NOT_FOUND)
        user.is_active = False
        user.save(update_fields=["is_active"])
        return success_response(message="User deactivated successfully.")


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer

    """
    POST /api/v1/auth/change-password/
    Allows a logged-in user to change their own password.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return success_response(message="Password changed successfully.")
