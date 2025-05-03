from django.db import models
from utils.mixins import AuditableMixin
from django.utils.timezone import datetime


# Create your models here.
class Products(AuditableMixin):
    """Main product model representing sellable items"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=False)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True,
                                 related_name='products') # null=True allows null values in the database.

    def __str__(self):
        return self.name


class Category(AuditableMixin):
    """Product categorization system"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

