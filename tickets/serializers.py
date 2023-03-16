import math

from rest_framework import serializers

from .models import (
    OrderTicket,
    TicketHistory,
    TicketComment,
    RequestTicket,
    InternalTicket,
    BaseTicket,
    TicketChecklistItem,
    OrderedProduct,
)
from common.serializers import FileSerializer
from .utils import get_changed_fields


class TicketSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseTicket
        fields = ("id", "title", "status", "ticket_type")


class BaseTicketSerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(required=False)
    labels = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    documents = FileSerializer(many=True, read_only=True)
    checklist_complete_percent = serializers.SerializerMethodField()

    class Meta:
        model = BaseTicket
        fields = "__all__"
        extra_kwargs = {
            'ticket_type': {'required': False},
            'status': {'required': False},
            'parent': {'write_only': True},
        }

    def get_checklist_complete_percent(self, instance):
        total = TicketChecklistItem.objects.filter(ticket=instance).count()
        if not total:
            return 100
        completed = TicketChecklistItem.objects.filter(
            ticket=instance, completed=True
        ).count()
        return math.ceil((completed * 100) / total)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr["linked_tickets"] = [
            {
                "id": t.id,
                "status": t.status,
                "title": t.title,
                "ticket_type": t.ticket_type,
            }
            for t in instance.linked_tickets.all()
        ]
        return repr

    def get_labels(self, instance):
        return list(instance.labels.all().values_list("name", flat=True))

    def get_tags(self, instance):
        return list(instance.tags.all().values_list("name", flat=True))

    def create(self, validated_data):
        parent = validated_data.pop("parent", None)
        ot = super().create(validated_data)
        h = TicketHistory.objects.create(
            updated_by=self.context["user"],
            description=f"Ticket was created by {self.context['user']}",
        )
        ot.history.add(h)
        if parent:
            linked_ticket = BaseTicket.objects.get(id=parent)
            ot.linked_tickets.add(linked_ticket)
        return ot

    def update(self, instance, validated_data):
        parent = validated_data.pop("parent", None)
        user = self.context["user"]
        changes = get_changed_fields(instance.__dict__, validated_data)
        obj = super().update(instance, validated_data)

        # capture history
        change_items = []
        for ch in changes:
            if not ch["old_value"]:
                change_items.append(f"added {ch['field']} {ch['new_value']}")
            else:
                change_items.append(
                    f"{ch['field']} changed from {str(ch['old_value'])} to {str(ch['new_value'])}"
                )
        h = TicketHistory.objects.create(
            updated_by=user, description=",".join(change_items)
        )
        instance.history.add(h)
        return obj


class OrderedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderedProduct
        fields = "__all__"


class OrderTicketSerializer(BaseTicketSerializer):
    products = OrderedProductSerializer(many=True, read_only=True)

    class Meta(BaseTicketSerializer.Meta):
        model = OrderTicket
        extra_kwargs = {
            **BaseTicketSerializer.Meta.extra_kwargs,
            'market_id': {'required': False},
        }


class TicketCommentSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data["added_by"] = self.context["user"]
        return super().create(validated_data)

    def to_representation(self, instance):
        d = super().to_representation(instance)
        d["added_by"] = instance.added_by.username
        return d

    class Meta:
        model = TicketComment
        fields = "__all__"
        extra_kwargs = {'added_by': {'required': False}}


class TicketHistorySerializer(serializers.ModelSerializer):
    updated_by = serializers.CharField(read_only=True, source='updated_by.username')

    class Meta:
        model = TicketHistory
        fields = "__all__"


class RequestTicketSerializer(BaseTicketSerializer):
    class Meta(BaseTicketSerializer.Meta):
        model = RequestTicket


class InternalTicketSerializer(BaseTicketSerializer):
    class Meta(BaseTicketSerializer.Meta):
        model = InternalTicket


class TicketChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketChecklistItem
        fields = "__all__"
        extra_kwargs = {
            'ticket': {'required': False, 'read_only': True},
        }

    def create(self, validated_data):
        validated_data["ticket"] = self.context["ticket"]
        return super().create(validated_data)
