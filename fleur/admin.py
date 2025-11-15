# fleur/admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import Distributor, Bouquet, Slot, Order, OrderStatus


class SlotInline(admin.TabularInline):
    model = Slot
    extra = 0
    fields = ("index", "label", "bouquet", "capacity", "quantity")
    autocomplete_fields = ("bouquet",)


@admin.register(Distributor)
class DistributorAdmin(admin.ModelAdmin):
    list_display = ("name", "serial_number", "location", "is_online", "last_heartbeat")
    search_fields = ("name", "serial_number", "location")
    list_filter = ("is_online",)
    inlines = [SlotInline]


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "image_preview")
    search_fields = ("name",)
    list_filter = ("price",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px;border-radius:4px;" />', obj.image.url)
        return "—"

    image_preview.short_description = "Aperçu"


@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("distributor", "index", "label", "bouquet", "capacity", "quantity")
    list_filter = ("distributor", "bouquet")
    search_fields = ("label", "distributor__name", "bouquet__name")
    autocomplete_fields = ("distributor", "bouquet")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "distributor",
        "slot",
        "amount",
        "inserted_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "distributor", "created_at")
    search_fields = ("id", "distributor__name", "slot__label")
    date_hierarchy = "created_at"
    autocomplete_fields = ("distributor", "slot")
    readonly_fields = ("created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("distributor", "slot")
