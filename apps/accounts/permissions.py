from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):

    message = "Administrator access is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "ADMIN"
            and request.user.is_active
        )


class IsEmployeeRole(BasePermission):

    message = "Employee access is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "EMPLOYEE"
            and request.user.is_active
        )
