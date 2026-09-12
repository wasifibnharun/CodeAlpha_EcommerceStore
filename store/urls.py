from django.urls import path

from . import views

app_name = "store"

urlpatterns = [
    path("health/", views.health_check, name="health_check"),
    path("", views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:product_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/<int:order_id>/success/", views.order_success, name="order_success"),
    path("orders/", views.order_history, name="order_history"),
]
