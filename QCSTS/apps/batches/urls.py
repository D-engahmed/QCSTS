from django.urls import path
from apps.batches import views

urlpatterns = [
    path("", views.BatchListCreateView.as_view(), name="batch-list-create"),
    path("<uuid:pk>/", views.BatchDetailView.as_view(), name="batch-detail"),
]
