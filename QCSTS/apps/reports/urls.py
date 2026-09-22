from django.urls import path
from .views import DashboardView, CSVExportView
from .analytics import AnalyticsView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
    path("export.csv", CSVExportView.as_view(), name="export-csv"),
]
