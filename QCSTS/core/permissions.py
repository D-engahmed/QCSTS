"""RBAC authorization derived only from the active Membership."""

from rest_framework.permissions import BasePermission

ROLE_RANK = {
    "viewer": 0,
    "read_only": 0,
    "analyst": 1,
    "reviewer": 2,
    "supervisor": 2,
    "qa_manager": 3,
    "site_admin": 4,
    "admin": 4,
    "organization_admin": 4,
    "billing_admin": 4,
}


class _MembershipPermission(BasePermission):
    def _membership(self, request):
        membership = getattr(request, "membership", None)
        if membership is None:
            raise RuntimeError(
                f"{self.__class__.__name__} requires fixed tenant context. "
                "The view must inherit a tenant-scoped base class."
            )
        return membership


class HasTenantContext(_MembershipPermission):
    message = "An active customer assignment is required."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and self._membership(request))


class MinimumRole(_MembershipPermission):
    min_role = "viewer"
    message = "Your assigned role is not sufficient for this action."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        role_name = (self._membership(request).role.name or "").strip().lower()
        return role_name in ROLE_RANK and ROLE_RANK[role_name] >= ROLE_RANK[self.min_role]


class IsViewer(MinimumRole):
    min_role = "viewer"


class IsAnalystOrAbove(MinimumRole):
    min_role = "analyst"


class IsReviewerOrAbove(MinimumRole):
    min_role = "reviewer"


class IsQAManager(MinimumRole):
    min_role = "qa_manager"


class IsAdmin(MinimumRole):
    min_role = "admin"

    def has_permission(self, request, view):
        membership = self._membership(request)
        return (
            super().has_permission(request, view)
            and membership.role.scope == "ORGANIZATION"
        )


class HasOrganizationPermission(_MembershipPermission):
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


class HasOrganizationScope(_MembershipPermission):
    message = "An organization-scoped role is required for this action."

    def has_permission(self, request, view):
        return self._membership(request).role.scope == "ORGANIZATION"
