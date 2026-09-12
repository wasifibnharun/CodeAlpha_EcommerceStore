from django.contrib import admin

from .models import Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "is_active")
    list_filter = ("is_active",)
    list_editable = ("price", "stock", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "user", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    list_editable = ("status",)
    search_fields = ("full_name", "email", "user__username")
    inlines = (OrderItemInline,)
