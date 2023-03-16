import django_filters

from .models import BaseTicket


class BaseTicketFilter(django_filters.FilterSet):
    class Meta:
        model = BaseTicket
        fields = ("status",)
