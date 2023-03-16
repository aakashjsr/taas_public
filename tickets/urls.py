from django.urls import path, include
from rest_framework import routers

from .views import (
    OrderTicketViewset,
    TicketCommentView,
    TicketCommentDocumentView,
    TicketDocumentView,
    TicketDocumentObjectView,
    InternalTicketViewset,
    RequestTicketViewset,
    TicketLabelView,
    TicketTagView,
    TicketHistoryView,
    TicketChecklistView,
    TicketChecklistObjectView,
    TicketSearchView,
    ExternalOrderDetails,
    DHLLabelView,
)

router = routers.DefaultRouter()
router.register('order-tickets', OrderTicketViewset)
router.register('request-tickets', RequestTicketViewset)
router.register('internal-tickets', InternalTicketViewset)


urlpatterns = [
    path('', include(router.urls)),
    # TODO: write unit test case for this
    path('external-orders/<int:id>/', ExternalOrderDetails.as_view()),
    path('search/', TicketSearchView.as_view()),
    path('<int:pk>/comments/', TicketCommentView.as_view()),
    path('<int:pk>/checklist/', TicketChecklistView.as_view()),
    path('checklist/<int:pk>/', TicketChecklistObjectView.as_view()),
    path('<int:pk>/history/', TicketHistoryView.as_view()),
    path('<int:pk>/documents/', TicketDocumentView.as_view()),
    path('<int:pk>/labels/', TicketLabelView.as_view()),
    path('<int:pk>/tags/', TicketTagView.as_view()),
    path('documents/<int:pk>/', TicketDocumentObjectView.as_view()),
    path('comments/<int:pk>/documents/', TicketCommentDocumentView.as_view()),
    path('generate-dhl-label/<int:pk>/', DHLLabelView.as_view()),
]
