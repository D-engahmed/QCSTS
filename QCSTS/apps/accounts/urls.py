from django.urls import path
from apps.accounts import views

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("me/", views.MeView.as_view(), name="me"),
    path("users/", views.UserListCreateView.as_view(), name="user-list-create"),
    path("users/<uuid:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change-password"),
]