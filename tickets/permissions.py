import datetime

from rest_framework.permissions import BasePermission
from accounts.constants import UserTypeChoice


class TicketDocumentObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != "DELETE":
            return True

        if request.user.user_type == UserTypeChoice.admin.value:
            return True
        elif request.user.user_type == UserTypeChoice.customer_care.value:
            current_dt = datetime.datetime.now()
            return (current_dt - obj.created_at.replace(tzinfo=None)).seconds < 5 * 60
        else:
            return False
