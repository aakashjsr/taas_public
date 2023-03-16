from django.contrib import admin
from tickets import models


class TicketHistory(admin.TabularInline):
    model = models.TicketHistory


class TicketCommentInline(admin.TabularInline):
    model = models.TicketComment


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Label)
class LabelAdmin(admin.ModelAdmin):
    pass


@admin.register(models.InternalTicket)
class InternalTicketAdmin(admin.ModelAdmin):
    list_display = ("title", "status")


@admin.register(models.RequestTicket)
class RequestTicketAdmin(admin.ModelAdmin):
    list_display = ("title", "status")


class OrderProductInline(admin.TabularInline):
    model = models.OrderedProduct


@admin.register(models.OrderTicket)
class OrderTicketAdmin(admin.ModelAdmin):
    list_display = ("title", "status")
    inlines = [
        OrderProductInline,
    ]


@admin.register(models.OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    pass
