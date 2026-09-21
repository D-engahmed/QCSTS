from django.urls import path
from apps.accounts import recovery, views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
    path("users/", views.UserListCreateView.as_view(), name="user-list-create"),
    path("users/<uuid:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("password-reset/", recovery.PasswordResetRequestView.as_view(), name="password-reset"),
    path("password-reset/confirm/", recovery.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("verify-email/", recovery.VerifyEmailView.as_view(), name="verify-email"),
]
