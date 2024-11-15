from rest_framework import permissions
from users.models import EmployerProfile
from rest_framework.exceptions import PermissionDenied


class HasEmployerProfilePermission(permissions.BasePermission):
    """
    Custom permission to only allow access to users who have an EmployerProfile.
    """

    def has_permission(self, request, view):
        return EmployerProfile.objects.filter(user=request.user).exists()
