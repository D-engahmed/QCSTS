import pytest
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.tests.factories import AdminFactory
from apps.reports.analytics import AnalyticsView
from apps.reports.views import CSVExportView, DashboardView


def tenant_request(user, path, query_string=""):
    factory = APIRequestFactory()
    request = factory.get(path + query_string)
    force_authenticate(request, user=user)
    request.organization = user.memberships.select_related("organization").get().organization
    return request


@pytest.mark.django_db
def test_dashboard_and_analytics_empty_tenant():
    user = AdminFactory()
    request = tenant_request(user, "/api/v1/reports/dashboard/")
    response = DashboardView().get(request)
    assert response.status_code == 200

    request = tenant_request(user, "/api/v1/reports/analytics/")
    response = AnalyticsView().get(request)
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize("resource", ["results", "batches", "test-points", "quality", "unsupported"])
def test_csv_export_resource_matrix(resource):
    user = AdminFactory()
    request = tenant_request(
        user,
        "/api/v1/reports/export/",
        f"?resource={resource}",
    )
    response = CSVExportView().get(request)
    if resource == "unsupported":
        assert response.status_code == 400
    else:
        assert response.status_code == 200
        assert "text/csv" in response["Content-Type"]
        assert response["Content-Disposition"].startswith("attachment;")
