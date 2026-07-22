from django.urls import path
from apps.schedule import views

urlpatterns = [
    path("", views.TestPointListView.as_view(), name="test-point-list"),
    path("<uuid:pk>/", views.TestPointDetailView.as_view(), name="test-point-detail"),
]
