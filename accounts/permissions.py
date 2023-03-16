from rest_framework.permissions import IsAuthenticated

from .constants import UserTypeChoice


class AppAdminPermission(IsAuthenticated):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and request.user.user_type == UserTypeChoice.admin.value
        )
