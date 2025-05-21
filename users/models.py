from django.db import models
from utils.mixins import AuditableMixin
# Create your models here.

class User(AuditableMixin):
    """Core user model representing system users"""
    name = models.CharField(max_length=100)

    def __str__(self):
        # Returns the user's name when displaying instances in admin or debugging
        return self.name


class Profile(AuditableMixin):
    """Additional user profile information"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=25, unique=True)

    def __str__(self):
        return f"{self.user.name}'s profile"

