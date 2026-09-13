from rest_framework.permissions import BasePermission

from apps.platform.services import TenantContextService


class HasTenantContext(BasePermission):
    message = "An active organization membership is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        TenantContextService.resolve(request)
        return True


class HasOrganizationPermission(HasTenantContext):
    permission_code = None

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.membership.has_permission(self.permission_code)
