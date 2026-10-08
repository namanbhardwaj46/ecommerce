from django.db import models
from utils.mixins import AuditableMixin
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser, AuditableMixin):
    """
        Core user model representing system users.
        Django's AbstractUser already inherits the password field and the secure password methods.

    """
    username = None
    email = models.EmailField(max_length=25, unique=True, null=True, blank=True,)
    is_verified = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        # Returns the user's name when displaying instances in admin or debugging
        return self.get_full_name() or self.email  or f"User {self.pk}"

# ForiegnKey: 1:M
# manytomany: M:M
# OneToOne: 1:1
# ManyToOne: M:1


class Profile(AuditableMixin):
    """Additional user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, unique=True, null=True)
    # email = models.EmailField(max_length=25, unique=True)

    def __str__(self):
        display_name = (
                self.user.get_full_name()
                or self.user.email
                or f"User {self.user_id}"
        )
        return f"{display_name}'s profile"
