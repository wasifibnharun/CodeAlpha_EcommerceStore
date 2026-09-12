from decimal import Decimal

from .models import Product


class Cart:
    SESSION_KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        self.data = self.session.get(self.SESSION_KEY, {})

    def add(self, product, quantity=1):
        product_id = str(product.pk)
        current = int(self.data.get(product_id, 0))
        self.data[product_id] = min(current + quantity, product.stock)
        self._save()

    def remove(self, product):
        self.data.pop(str(product.pk), None)
        self._save()

    def update(self, product, quantity):
        product_id = str(product.pk)
        if quantity <= 0:
            self.data.pop(product_id, None)
        else:
            self.data[product_id] = min(quantity, product.stock)
        self._save()

    def clear(self):
        self.session.pop(self.SESSION_KEY, None)
        self.session.modified = True

    def items(self):
        products = Product.objects.filter(id__in=self.data.keys(), is_active=True)
        rows = []
        for product in products:
            quantity = min(int(self.data[str(product.pk)]), product.stock)
            if quantity:
                rows.append({
                    "product": product,
                    "quantity": quantity,
                    "subtotal": product.price * quantity,
                })
        return rows

    def total(self):
        return sum((row["subtotal"] for row in self.items()), Decimal("0.00"))

    def count(self):
        return sum(row["quantity"] for row in self.items())

    def _save(self):
        self.session[self.SESSION_KEY] = self.data
        self.session.modified = True
