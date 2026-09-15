"""
Organization-scoped authorization.

What changed and why
--------------------
These classes previously read ``request.user.role`` — a single CharField on
CustomUser with no organization dimension. That meant one "admin" was an admin
of *every* tenant on the platform, and ``UserDetailView.patch`` could hand that
role to anyone. Meanwhile the real RBAC model (Membership -> Role ->
Permission) sat in apps/platform with zero call sites.

Two authorization systems is worse than one bad one. There is now exactly one:
authority comes from the Membership that ``TenantContextService`` verified for
the active organization. ``CustomUser.role`` is no longer consulted for any
access decision.

Ordering: these classes require ``request.membership``, which
``TenantScopedAPIView.perform_authentication`` sets before DRF runs
``check_permissions``. Using them on a plain APIView is a programming error and
raises loudly rather than failing open.
"""

from rest_framework.permissions import BasePermission

# Ranked role ladder. Names match platform.Role.name.
ROLE_RANK = {
    "viewer": 0,
    "analyst": 1,
    "supervisor": 2,
    "qa_manager": 3,
    "admin": 4,
    "system": 4,
}


class _MembershipPermission(BasePermission):
    """Shared plumbing: pull the verified membership off the request."""

    def _membership(self, request):
        membership = getattr(request, "membership", None)
        if membership is None:
            raise RuntimeError(
                f"{self.__class__.__name__} requires tenant context. "
                "The view must inherit core.views.TenantScopedAPIView."
            )
        return membership


class HasTenantContext(_MembershipPermission):
    message = "An active organization membership is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return self._membership(request) is not None


class MinimumRole(_MembershipPermission):
    """
    Grants access when the membership's role ranks at or above ``min_role``.

    Rank is evaluated inside the active organization only. A user who is admin
    of org A and analyst of org B gets analyst authority while org B is the
    active context.
    """

    min_role = "viewer"
    message = "Your role in this organization is not sufficient for this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        membership = self._membership(request)
        role_name = (membership.role.name or "").strip().lower()
        if role_name not in ROLE_RANK:
            return False
        return ROLE_RANK[role_name] >= ROLE_RANK[self.min_role]


class IsViewer(MinimumRole):
    min_role = "viewer"
    message = "Authentication and an organization membership are required."


class IsAnalystOrAbove(MinimumRole):
    min_role = "analyst"
    message = "Analyst role or above is required for this action."


class IsReviewerOrAbove(MinimumRole):
    min_role = "supervisor"
    message = "Supervisor role or above is required for this action."


class IsQAManager(MinimumRole):
    min_role = "qa_manager"
    message = "QA Manager role or above is required for this action."


class IsAdmin(MinimumRole):
    min_role = "admin"
    message = "Administrator role is required for this action."


class HasOrganizationPermission(_MembershipPermission):
    """
    Fine-grained check against the Permission catalogue.

    Prefer this over role rank for anything that customers will want to
    reconfigure (they will). Set ``permission_code`` on a subclass.
    """

    permission_code = None
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if self.permission_code is None:
            raise RuntimeError(
                f"{self.__class__.__name__} must define permission_code."
            )
        return self._membership(request).has_permission(self.permission_code)
