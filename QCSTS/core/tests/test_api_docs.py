"""Regression tests for the public OpenAPI/Swagger endpoints."""

from django.urls import reverse


def test_swagger_ui_is_available_with_or_without_trailing_slash(client):
    for path in ("/api/docs", "/api/docs/"):
        response = client.get(path)
        assert response.status_code == 200, response.content
        assert "swagger-ui" in response.content.decode().lower()


def test_openapi_schema_is_available_with_or_without_trailing_slash(client):
    for path in ("/api/schema", "/api/schema/"):
        response = client.get(path)
        assert response.status_code == 200, response.content
        assert response["Content-Type"].startswith("application/vnd.oai.openapi")
        payload = response.json()
        assert payload["openapi"].startswith("3.")
        assert payload["info"]["title"] == "QCSTS API"
