from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/v1/products/", include("apps.products.urls")),
    path("api/v1/batches/", include("apps.batches.urls")),
    path("api/v1/test-points/", include("apps.schedule.urls")),
    path("api/v1/results/", include("apps.results.urls")),
    path("api/v1/chamber/", include("apps.chamber.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/audit/", include("apps.audit.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
