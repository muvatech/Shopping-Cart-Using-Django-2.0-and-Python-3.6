from decimal import Decimal

from django.db import models
from django.db.models import F, Sum
from shop.models import Product


class InsufficientStockError(Exception):
    """Raised when an order can't be fulfilled because a product lacks stock."""

    def __init__(self, product):
        self.product = product
        super().__init__(
            'Insufficient stock for {}'.format(product.name)
        )


class Order(models.Model):
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField()
    address = models.CharField(max_length=150)
    postal_code = models.CharField(max_length=30)
    city = models.CharField(max_length=100)
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return self.total_cost

    def calculate_total_cost(self):
        """Recompute the total cost from related OrderItems (DB-side aggregation)."""
        total = self.items.aggregate(
            total=Sum(
                F('price') * F('quantity'),
                output_field=models.DecimalField(
                    max_digits=12, decimal_places=2),
            )
        )['total']
        return total if total is not None else Decimal('0')


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity
