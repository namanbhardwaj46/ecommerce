from django.db import models
from django.utils.timezone import datetime


# Create your models here.

class AuditableMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True) # Set only once at creation time.
                                                        # datetime.now() : It can also be used.
    updated_at = models.DateTimeField(auto_now=True) # Update automatically on save.

    # created_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_created_by', on_delete=models.CASCADE)
    # updated_by = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_updated_by', on_delete=models.CASCADE)
    class Meta:
        abstract = True


class User(AuditableMixin):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Profile(AuditableMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=25, unique=True)

    def __str__(self):
        return f"{self.user.name}'s profile"


class Products(AuditableMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=False)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True,
                                 related_name='products') # null=True allows null values in the database.

    def __str__(self):
        return self.name


class Category(AuditableMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Orders(AuditableMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Products, through='OrderItems', related_name='orders')


class OrderItems(AuditableMixin):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1) # Ensure every order item has at least 1 product. Track product quantity.
    price_at_time = models.DecimalField(max_digits=8, decimal_places=2)  # Price of the product when ordered
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)  # price_at_time * quantity

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def save(self, *args, **kwargs):
        # Calculate subtotal before saving
        self.subtotal = self.price_at_time * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"