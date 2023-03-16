from django.db.models import Q
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveDestroyAPIView,
    RetrieveAPIView,
    ListAPIView,
    UpdateAPIView,
)

from common.connectors.plentymarket.plentymarket_adaptor import PlentyMarketAPI
from common.models import File
from common.views import DocumentListUploadView
from common.serializers import FileSerializer
from .filters import BaseTicketFilter
from .permissions import TicketDocumentObjectPermission
from .serializers import (
    OrderTicketSerializer,
    TicketCommentSerializer,
    RequestTicketSerializer,
    InternalTicketSerializer,
    TicketHistorySerializer,
    TicketChecklistItemSerializer,
    TicketSearchSerializer,
    OrderedProductSerializer,
)
from .models import (
    OrderTicket,
    BaseTicket,
    TicketHistory,
    TicketComment,
    RequestTicket,
    InternalTicket,
    Label,
    Tag,
    TicketChecklistItem,
)
from .utils import (
    dhl_return_label_from_order_ticket,
    dhl_shipping_label_from_order_ticket,
)


class TicketSearchView(ListAPIView):
    queryset = BaseTicket.objects.all()
    serializer_class = TicketSearchSerializer
    pagination_class = None

    def get_queryset(self):
        q = self.request.GET.get("query", "")
        if not q:
            return BaseTicket.objects.none()
        return BaseTicket.objects.filter(Q(title__icontains=q) | Q(id__icontains=q))


class OrderTicketViewset(ModelViewSet):
    serializer_class = OrderTicketSerializer
    queryset = OrderTicket.objects.all().prefetch_related('products')

    filterset_class = BaseTicketFilter

    def get_serializer_context(self):
        return {"user": self.request.user}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            order_ticket = serializer.save()
            products = [
                {**i, "order_ticket": order_ticket}
                for i in request.data.get("products", [])
            ]
            product_serializer = OrderedProductSerializer(data=products, many=True)
            product_serializer.is_valid(raise_exception=True)
            product_serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class RequestTicketViewset(ModelViewSet):
    serializer_class = RequestTicketSerializer
    filterset_class = BaseTicketFilter
    queryset = RequestTicket.objects.all()

    def get_serializer_context(self):
        return {"user": self.request.user}


class InternalTicketViewset(ModelViewSet):
    serializer_class = InternalTicketSerializer
    queryset = InternalTicket.objects.all()
    filterset_class = BaseTicketFilter

    def get_serializer_context(self):
        return {"user": self.request.user}


class TicketCommentView(ListCreateAPIView):
    serializer_class = TicketCommentSerializer
    pagination_class = None

    def get_queryset(self):
        ticket = get_object_or_404(BaseTicket, pk=self.kwargs["pk"])
        return ticket.comments.all()

    def perform_create(self, serializer):
        comment = serializer.save()
        ticket = get_object_or_404(BaseTicket, pk=self.kwargs["pk"])
        ticket.comments.add(comment)
        h = TicketHistory.objects.create(
            description=f"{self.request.user} added a comment",
            updated_by=self.request.user,
        )
        ticket.history.add(h)

    def get_serializer_context(self):
        return {"user": self.request.user}


class TicketHistoryView(ListAPIView):
    serializer_class = TicketHistorySerializer
    pagination_class = None

    def get_queryset(self):
        ticket = get_object_or_404(BaseTicket, pk=self.kwargs["pk"])
        return ticket.history.all()


class TicketDocumentView(DocumentListUploadView):
    def get_is_public(self):
        return False

    def get_sub_folder(self):
        return "ticket_documents"

    def get_model(self):
        return BaseTicket


class TicketDocumentObjectView(RetrieveDestroyAPIView):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = (TicketDocumentObjectPermission,)


class TicketCommentDocumentView(DocumentListUploadView):
    def get_is_public(self):
        return False

    def get_sub_folder(self):
        return "ticket_comments_documents"

    def get_model(self):
        return TicketComment


class TicketTagView(RetrieveAPIView):
    queryset = BaseTicket.objects.all()

    def get(self, request, *args, **kwargs):
        ticket = self.get_object()
        return Response(ticket.tags.all().values_list("name", flat=True))

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        tag_name = request.data.get("name")
        if not tag_name:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        tag, _ = Tag.objects.get_or_create(
            name__iexact=tag_name, defaults={"name": tag_name}
        )
        ticket.tags.add(tag)
        return Response({})

    def patch(self, request, *args, **kwargs):
        ticket = self.get_object()
        tag = Tag.objects.filter(name=request.data.get("name", "")).first()
        if not tag:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ticket.tags.remove(tag)
        return Response({})


class TicketLabelView(RetrieveAPIView):
    queryset = BaseTicket.objects.all()

    def get(self, request, *args, **kwargs):
        ticket = self.get_object()
        return Response(ticket.labels.all().values_list("name", flat=True))

    def post(self, request, *args, **kwargs):
        ticket = self.get_object()
        label_name = request.data.get("name")
        if not label_name:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        label, _ = Label.objects.get_or_create(
            name__iexact=label_name, defaults={"name": label_name}
        )
        ticket.labels.add(label)
        return Response({})

    def patch(self, request, *args, **kwargs):
        ticket = self.get_object()
        label = Label.objects.filter(name=request.data.get("name", "")).first()
        if not label:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ticket.labels.remove(label)
        return Response({})


class TicketChecklistView(ListCreateAPIView):
    pagination_class = None
    serializer_class = TicketChecklistItemSerializer

    def get_queryset(self):
        ticket = get_object_or_404(BaseTicket, pk=self.kwargs["pk"])
        return ticket.checklist_items.all()

    def get_serializer_context(self):
        return {"ticket": get_object_or_404(BaseTicket, pk=self.kwargs["pk"])}


class TicketChecklistObjectView(UpdateAPIView):
    queryset = TicketChecklistItem.objects.all()
    serializer_class = TicketChecklistItemSerializer


class ExternalOrderDetails(RetrieveAPIView):
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, *args, **kwargs):
        order_id = kwargs["id"]
        connector = PlentyMarketAPI()
        details = connector.get_order_details(order_id)
        if details is None:
            return Response(status=404)
        return Response(details)


class DHLLabelView(RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        order_ticket = OrderTicket.objects.get(id=kwargs["pk"])
        label_type = request.GET.get("label_type")

        if label_type == "return_label":
            if order_ticket.dhl_return_label_data:
                return Response(
                    {"label_base64_data": order_ticket.dhl_return_label_data}
                )
            updated_ticket = dhl_return_label_from_order_ticket(order_ticket)
            if not updated_ticket:
                return Response({"details": "Missing data"}, status=400)
            return Response({"label_base64_data": updated_ticket.dhl_return_label_data})

        elif label_type == "shipping_label":
            if order_ticket.dhl_shipping_label_data:
                return Response(
                    {"label_base64_data": order_ticket.dhl_shipping_label_data}
                )
            updated_ticket = dhl_shipping_label_from_order_ticket(order_ticket)
            if not updated_ticket:
                return Response({"details": "Missing data"}, status=400)
            return Response(
                {"label_base64_data": updated_ticket.dhl_shipping_label_data}
            )
        return Response({"details": "Invalid label type"}, status=400)
