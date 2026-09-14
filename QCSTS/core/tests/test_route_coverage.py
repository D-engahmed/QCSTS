"""
Structural guarantee for tenant isolation.

The gap checklist lists ~25 separate "X isolation" boxes — Product, Batch,
Chamber, TestPoint, SamplePull, TestResult, Report, Audit, Export, Dashboard...
Ticking those one model at a time is what produced the accounts leak: the
discipline held for eleven views and failed on the twelfth, and nothing caught
it.

This test makes the boxes structural instead. Every route registered in the
URLconf must be either tenant scoped or on an explicit, justified exemption
list. A new endpoint added in Phase 2 that forgets to inherit
TenantScopedAPIView fails CI on the commit that introduces it, not in a
customer's audit.
"""

import pytest
from django.urls import URLPattern, URLResolver, get_resolver

from core.views import TenantExemptAPIView, TenantScopedAPIView

# Routes that legitimately have no organization context. Each entry needs a
# reason; "it was easier" is not one.
EXEMPT_PREFIXES = (
    "admin/",              # Django admin — staff-only, outside the tenant API
    "api/schema/",         # OpenAPI schema document
    "api/docs/",           # Swagger UI
    "api/v1/auth/token/",  # SimpleJWT refresh — issues tokens, reads no tenant data
)


def _walk(patterns, prefix=""):
    for entry in patterns:
        if isinstance(entry, URLResolver):
            yield from _walk(entry.url_patterns, prefix + str(entry.pattern))
        elif isinstance(entry, URLPattern):
            yield prefix + str(entry.pattern), entry.callback


def _api_routes():
    for route, callback in _walk(get_resolver().url_patterns):
        if route.startswith(EXEMPT_PREFIXES):
            continue
        cls = getattr(callback, "cls", None) or getattr(callback, "view_class", None)
        if cls is None:
            continue
        yield route, cls


def test_the_walker_actually_finds_routes():
    """Guards against the coverage test silently passing because it found nothing."""
    routes = list(_api_routes())
    assert len(routes) >= 15, f"Route walker found only {len(routes)} views — it is broken."


@pytest.mark.parametrize("route,cls", list(_api_routes()), ids=lambda v: str(v))
def test_every_route_declares_its_tenant_posture(route, cls):
    if isinstance(route, type):
        pytest.skip("parametrize id artefact")

    scoped = issubclass(cls, TenantScopedAPIView)
    exempt = issubclass(cls, TenantExemptAPIView)

    assert scoped or exempt, (
        f"{cls.__module__}.{cls.__name__} (route: {route}) inherits plain APIView. "
        "Every endpoint must declare its tenant posture: inherit "
        "core.views.TenantScopedAPIView for organization-owned data, or "
        "core.views.TenantExemptAPIView with a docstring explaining why it has "
        "no organization context."
    )
    assert not (scoped and exempt), (
        f"{cls.__name__} claims to be both tenant scoped and tenant exempt."
    )


def test_exempt_views_document_their_reason():
    for route, cls in _api_routes():
        if issubclass(cls, TenantExemptAPIView):
            assert (cls.__doc__ or "").strip(), (
                f"{cls.__name__} opts out of tenant scoping but gives no reason. "
                "Add a docstring stating why it has no organization context."
            )
