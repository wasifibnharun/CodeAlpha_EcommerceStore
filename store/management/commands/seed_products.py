from django.core.management.base import BaseCommand

from store.models import Product


PRODUCTS = [
    {
        "name": "Everyday Backpack",
        "slug": "everyday-backpack",
        "description": "A lightweight, durable backpack with room for a laptop and daily essentials.",
        "price": "2490.00",
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Wireless Headphones",
        "slug": "wireless-headphones",
        "description": "Comfortable over-ear headphones with clear sound and long battery life.",
        "price": "3890.00",
        "stock": 8,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80",
    },
    {
        "name": "Classic Wristwatch",
        "slug": "classic-wristwatch",
        "description": "A minimal everyday watch with a timeless dial and comfortable leather strap.",
        "price": "3200.00",
        "stock": 10,
        "image_url": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?auto=format&fit=crop&w=900&q=80",
    },
]


class Command(BaseCommand):
    help = "Create or refresh the demo product catalog."

    def handle(self, *args, **options):
        for values in PRODUCTS:
            Product.objects.update_or_create(slug=values["slug"], defaults=values)
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(PRODUCTS)} demo products."))
