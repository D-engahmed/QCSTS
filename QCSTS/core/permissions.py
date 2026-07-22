from rest_framework.permissions import BasePermission

class IsViewer(BasePermission):
    message = "Authentication required."
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class IsAnalystOrAbove(BasePermission):
    message = "Analyst role or above is required for this action."
    ALLOWED_ROLES = {"admin", "qa_manager", "supervisor", "analyst", "system"}
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ALLOWED_ROLES
        )

class IsReviewerOrAbove(BasePermission):
    message = "Supervisor role or above is required for this action."
    ALLOWED_ROLES = {"admin", "qa_manager", "supervisor"}
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ALLOWED_ROLES
        )

class IsQAManager(BasePermission):
    message = "QA Manager role or above is required for this action."
    ALLOWED_ROLES = {"admin", "qa_manager"}
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in self.ALLOWED_ROLES
        )

class IsAdmin(BasePermission):
    message = "Administrator role is required for this action."
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )