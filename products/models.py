from django.db import models
from utils.mixins import AuditableMixin
from django.utils.timezone import datetime


# Create your models here.

class Category(AuditableMixin):
    """Product categorization system"""
    name = models.CharField(
        max_length=100,  # Restricts the category name to 100 characters
        unique=True  # Enforces uniqueness to prevent duplicate category names
    )

    def __str__(self):
        # Returns the category name when displaying instances in admin or debugging
        return self.name

class Product(AuditableMixin):
    """Main product model representing sellable items"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=False)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True,
                                 related_name='products') # null=True allows null values in the database.
    stock_quantity = models.PositiveIntegerField(
        default=0,  # Sets default stock to 0
        verbose_name="Stock Quantity",  # Label for admin and UI
        help_text="Tracks the number of units available in inventory"  # Clarifies the field's purpose
    )

    class Meta:
        ordering = ['-created_at']  # Displays newest products first in query results

    def __str__(self):
        # Returns a meaningful representation of the product for admin or debugging
        return f"{self.name} (₹{self.price})"

