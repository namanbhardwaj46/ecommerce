from django.db import models
from django.utils.timezone import datetime
from products.utility import AuditableMixin


# Create your models here.

# class Products(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     price = models.DecimalField(max_digits=5, decimal_places=2)
#     is_available = models.BooleanField(default=False)
#     created_at = models.DateTimeField(default=datetime.now)


class Products(AuditableMixin):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=False)

