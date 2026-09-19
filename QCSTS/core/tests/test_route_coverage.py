"""Structural security guarantees for the API route surface."""

import pytest
from django.urls import URLPattern, URLResolver, get_resolver
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.views import TenantExemptAPIView, TenantScopedAPIView, TenantExemptViewSet, TenantScopedViewSet

EXEMPT_PREFIXES = (
    "admin/",
    "api/v1/auth/token/",
)


def _is_exempt_route(route):
    return (
        any(route == prefix or route.startswith(prefix) for prefix in EXEMPT_PREFIXES)
        or route in {"api/schema", "api/docs"}
        or route.startswith("api/schema/")
        or route.startswith("api/docs/")
    )


def _walk(patterns, prefix=""):
    for entry in patterns:
        if isinstance(entry, URLResolver):
            yield from _walk(entry.url_patterns, prefix + str(entry.pattern))
        elif isinstance(entry, URLPattern):
            yield prefix + str(entry.pattern), entry.callback


def _api_routes():
    for route, callback in _walk(get_resolver().url_patterns):
        if _is_exempt_route(route):
            continue
        cls = getattr(callback, "cls", None) or getattr(callback, "view_class", None)
        if cls is not None:
            yield route, cls


def test_the_walker_actually_finds_routes():
    routes = list(_api_routes())
    assert len(routes) >= 15, f"Route walker found only {len(routes)} views — it is broken."


@pytest.mark.parametrize("route,cls", list(_api_routes()), ids=lambda v: str(v))
def test_every_route_declares_tenant_posture(route, cls):
    scoped = issubclass(cls, (TenantScopedAPIView, TenantScopedViewSet))
    exempt = issubclass(cls, (TenantExemptAPIView, TenantExemptViewSet))

    assert scoped or exempt, (
        f"{cls.__module__}.{cls.__name__} (route: {route}) inherits plain APIView. "
        "Every endpoint must explicitly declare tenant posture."
    )
    assert not (scoped and exempt), f"{cls.__name__} claims both tenant scoped and exempt."


@pytest.mark.parametrize("route,cls", list(_api_routes()), ids=lambda v: str(v))
def test_every_tenant_route_declares_action_authorization(route, cls):
    if not issubclass(cls, (TenantScopedAPIView, TenantScopedViewSet)):
        return

    declared = cls.__dict__.get("permission_classes")
    assert declared is not None, (
        f"{cls.__name__} ({route}) has no explicit permission_classes. "
        "Tenant endpoints must declare tenant-aware RBAC."
    )
    assert AllowAny not in declared, f"{cls.__name__} ({route}) cannot use AllowAny."
    assert declared != [IsAuthenticated], (
        f"{cls.__name__} ({route}) uses authentication without action authorization."
    )


def test_exempt_views_document_their_reason():
    for route, cls in _api_routes():
        if issubclass(cls, (TenantExemptAPIView, TenantExemptViewSet)):
            assert (cls.__doc__ or "").strip(), (
                f"{cls.__name__} opts out of tenant scoping but gives no reason."
            )
