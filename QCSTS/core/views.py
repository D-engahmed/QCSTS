"""
Tenant-scoped view base classes.

Why this exists
---------------
Before this module, tenant isolation was *opt-in*: every handler had to
remember to call ``TenantContextService.scope_queryset``. The accounts app
forgot, and leaked every user in every organization through
``/api/v1/auth/users/``.

Opt-in isolation fails open. A view that forgets the call serves cross-tenant
data and no test notices. This module inverts that: tenant context is resolved
in ``perform_authentication`` — before permission checks, before the handler —
so it is impossible for a subclass to run without it.

Anything that must NOT be tenant scoped (login, token refresh, schema) has to
inherit ``PublicAPIView`` or ``TenantExemptAPIView`` and say so explicitly.
``core/tests/test_route_coverage.py`` walks the URLconf and fails the build if
any route is neither scoped nor explicitly exempt.
"""

from rest_framework.views import APIView

from apps.platform.services import TenantContextService


class TenantExemptAPIView(APIView):
    """
    Explicitly opts out of tenant scoping.

    Use ONLY for endpoints that legitimately have no organization context:
    authentication entry points, self-service account endpoints, schema docs.
    Every subclass must state why in its docstring — the route coverage test
    reads this class as a deliberate declaration, not an oversight.
    """

    tenant_scoped = False


class PublicAPIView(TenantExemptAPIView):
    """Unauthenticated entry points (login, token refresh)."""


class TenantScopedAPIView(APIView):
    """
    Base class for every endpoint that touches organization-owned data.

    Guarantees, for every handler:
        request.organization    — the active Organization (never None)
        request.membership      — the verified Membership backing that context
        request.site            — the active Site, or None
        request.tenant_context  — the frozen TenantContext dataclass

    Resolution happens in ``perform_authentication``, which DRF calls at the
    top of ``initial()`` — before ``check_permissions``. Permission classes can
    therefore rely on ``request.membership`` existing.
    """

    tenant_scoped = True

    def perform_authentication(self, request):
        super().perform_authentication(request)
        if request.user and request.user.is_authenticated:
            TenantContextService.resolve(request)

    # ── Query scoping ────────────────────────────────────────────────────────

    def tenant_qs(self, queryset):
        """
        Restrict a queryset to the active organization.

        Prefer this over a hand-written ``.filter(organization=...)`` so that
        the scoping rule lives in one place and can be tightened later (for
        example, to add site scoping) without touching every view.
        """
        return queryset.filter(organization=self.request.organization)

    def site_qs(self, queryset, field="site"):
        """
        Restrict a queryset to the active site, on top of organization scoping.

        No-ops when the membership has no site restriction, so it is safe to
        apply unconditionally on site-aware models.
        """
        queryset = self.tenant_qs(queryset)
        site = getattr(self.request, "site", None)
        if site is None:
            return queryset
        return queryset.filter(**{field: site})

    # ── Write scoping ────────────────────────────────────────────────────────

    def tenant_create_kwargs(self, **extra):
        """
        Standard kwargs for ``serializer.save()`` on create.

        Never trust a client-supplied organization: it is injected here from
        the server-verified membership, so a payload carrying another tenant's
        organization ID is silently overridden rather than honoured.
        """
        kwargs = {
            "organization": self.request.organization,
            "created_by": self.request.user,
        }
        kwargs.update(extra)
        return kwargs
