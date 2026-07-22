from django.urls import path
from apps.audit import views

urlpatterns = [
    path("", views.AuditLogListView.as_view(), name="audit-list"),
    path("<uuid:pk>/", views.AuditLogDetailView.as_view(), name="audit-detail"),
]
