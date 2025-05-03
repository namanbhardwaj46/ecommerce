from django.db import models
from users.models import User
from products.models import Products
from utils.mixins import AuditableMixin


# Create your models here.

class Order(AuditableMixin):
    """Main order model handling transaction details"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order')
    products = models.ManyToManyField(Products, through='OrderProduct', related_name='order')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Track total amount of an order.

    class OrderStatus(models.TextChoices):
        PENDING = "pending", "Pending" # Order created but not paid yet
        SUCCESS = "success", "Success" # Payment Successful
        FAILED = "failed", "Failed" # Payment Failed

    status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.PENDING)


    def __str__(self):
        product_names = ", ".join([product.name for product in self.products.all()])
        return f"Order #{self.id} by {self.user.name} - Products: {product_names}"


class OrderProduct(AuditableMixin):
    """Through model for product-order relationship with pricing details"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1) # Ensure every order item has at least 1 product. Track product quantity.
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product when ordered
    line_total = models.DecimalField(max_digits=10, decimal_places=2)  # price_at_time * quantity

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs):
        # Calculate subtotal before saving
        self.line_total = self.price_at_time * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"