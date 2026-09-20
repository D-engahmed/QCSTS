from django.urls import path
from .views import DashboardView, CSVExportView

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("export.csv", CSVExportView.as_view(), name="export-csv"),
    path("export.csv/", CSVExportView.as_view(), name="export-csv-slash"),
]
