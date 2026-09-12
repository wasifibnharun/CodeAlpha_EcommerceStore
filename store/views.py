from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, RegisterForm
from .models import Category, Order, OrderItem, Product


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    categories = Category.objects.all()
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)

    return render(
        request,
        "store/product_list.html",
        {
            "products": products,
            "categories": categories,
            "query": query,
            "selected_category": category_slug,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, "store/product_detail.html", {"product": product})


def register(request):
    if request.user.is_authenticated:
        return redirect("store:product_list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account is ready.")
        return redirect("store:product_list")
    return render(request, "registration/register.html", {"form": form})


def cart_detail(request):
    cart = Cart(request)
    return render(request, "store/cart.html", {"cart_items": cart.items(), "cart_total": cart.total()})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if product.stock:
        Cart(request).add(product)
        messages.success(request, f"{product.name} was added to your cart.")
    else:
        messages.error(request, "This product is out of stock.")
    return redirect(request.POST.get("next") or "store:cart_detail")


@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Cart(request).remove(product)
    messages.info(request, f"{product.name} was removed from your cart.")
    return redirect("store:cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    Cart(request).update(product, quantity)
    messages.success(request, "Your cart was updated.")
    return redirect("store:cart_detail")


@login_required
def checkout(request):
    cart = Cart(request)
    cart_items = cart.items()
    if not cart_items:
        messages.info(request, "Your cart is empty.")
        return redirect("store:product_list")

    initial = {"full_name": request.user.get_full_name(), "email": request.user.email}
    form = CheckoutForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            locked_products = {
                product.pk: product
                for product in Product.objects.select_for_update().filter(
                    pk__in=[row["product"].pk for row in cart_items]
                )
            }
            for row in cart_items:
                product = locked_products[row["product"].pk]
                if product.stock < row["quantity"]:
                    messages.error(request, f"Not enough stock for {product.name}.")
                    return redirect("store:cart_detail")

            order = Order.objects.create(user=request.user, total=cart.total(), **form.cleaned_data)
            for row in cart_items:
                product = locked_products[row["product"].pk]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=row["quantity"],
                    price=product.price,
                )
                product.stock -= row["quantity"]
                product.save(update_fields=["stock"])

        cart.clear()
        return redirect("store:order_success", order_id=order.pk)

    return render(request, "store/checkout.html", {"form": form, "cart_items": cart_items, "cart_total": cart.total()})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_success.html", {"order": order})


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related("items__product")
    return render(request, "store/order_history.html", {"orders": orders})
