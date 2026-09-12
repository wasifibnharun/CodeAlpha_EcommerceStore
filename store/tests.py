from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, Product


class StoreFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("shopper", "shopper@example.com", "strong-pass-123")
        self.category = Category.objects.create(name="Accessories", slug="accessories")
        self.product = Product.objects.create(
            category=self.category,
            name="Test Product",
            slug="test-product",
            description="A product used by the automated tests.",
            price="250.00",
            stock=5,
        )

    def test_catalog_and_detail_pages(self):
        response = self.client.get(reverse("store:product_list"))
        self.assertContains(response, "Test Product")
        response = self.client.get(self.product.get_absolute_url())
        self.assertContains(response, "A product used by the automated tests.")

    def test_health_check(self):
        response = self.client.get(reverse("store:health_check"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_product_uses_remote_image_as_upload_fallback(self):
        self.product.image_url = "https://example.com/product.jpg"
        self.assertEqual(self.product.display_image, "https://example.com/product.jpg")

    def test_product_can_store_an_uploaded_image(self):
        gif = (
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00"
            b"\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
        )
        self.product.image = SimpleUploadedFile("product.gif", gif, content_type="image/gif")
        self.product.save(update_fields=["image"])
        self.assertIn("/media/products/", self.product.display_image)
        self.product.image.delete(save=False)

    def test_cart_add_requires_post(self):
        response = self.client.get(reverse("store:cart_add", args=[self.product.pk]))
        self.assertEqual(response.status_code, 405)

    def test_catalog_can_be_searched_and_filtered(self):
        response = self.client.get(reverse("store:product_list"), {"q": "Test", "category": "accessories"})
        self.assertContains(response, "Test Product")
        response = self.client.get(reverse("store:product_list"), {"q": "missing"})
        self.assertNotContains(response, "Test Product")

    def test_cart_quantity_can_be_updated(self):
        self.client.post(reverse("store:cart_add", args=[self.product.pk]))
        response = self.client.post(reverse("store:cart_update", args=[self.product.pk]), {"quantity": 3})
        self.assertRedirects(response, reverse("store:cart_detail"))
        self.assertEqual(self.client.session["cart"][str(self.product.pk)], 3)

    def test_authenticated_checkout_creates_order_and_reduces_stock(self):
        self.client.force_login(self.user)
        self.client.post(reverse("store:cart_add", args=[self.product.pk]))
        response = self.client.post(
            reverse("store:checkout"),
            {"full_name": "Test Shopper", "email": "shopper@example.com", "address": "Dhaka"},
        )
        order = Order.objects.get()
        self.assertRedirects(response, reverse("store:order_success", args=[order.pk]))
        self.assertEqual(order.items.get().quantity, 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)

    def test_user_cannot_view_another_users_order(self):
        other = User.objects.create_user("other", password="strong-pass-123")
        order = Order.objects.create(user=other, full_name="Other", email="other@example.com", address="Dhaka")
        self.client.force_login(self.user)
        response = self.client.get(reverse("store:order_success", args=[order.pk]))
        self.assertEqual(response.status_code, 404)

    def test_order_history_only_lists_current_users_orders(self):
        other = User.objects.create_user("another", password="strong-pass-123")
        own_order = Order.objects.create(user=self.user, full_name="Shopper", email="shopper@example.com", address="Dhaka")
        Order.objects.create(user=other, full_name="Another", email="another@example.com", address="Dhaka")
        self.client.force_login(self.user)
        response = self.client.get(reverse("store:order_history"))
        self.assertContains(response, f"Order #{own_order.pk}")
        self.assertNotContains(response, "Another")
