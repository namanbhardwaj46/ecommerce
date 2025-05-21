from django.db import models
from utils.mixins import AuditableMixin
from orders.models import Order
import uuid


# Create your models here.

class Payment(AuditableMixin):

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESSFUL = 'successful', 'Successful'
        FAILED = 'failed', 'Failed'

    class PaymentMethod(models.TextChoices):
        Wallet = 'wallet', 'Wallet'
        UPI = 'upi', 'UPI'
        CARD = 'card', 'Credit/Debit Card'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(choices=PaymentStatus.choices, max_length=20, default=PaymentStatus.PENDING)
    method = models.CharField(choices=PaymentMethod.choices, max_length=20)
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    gateway = models.CharField(max_length=50, help_text="Name of the payment gateway used")
    raw_response = models.JSONField(default=dict, help_text="Full JSON response/payload received from the payment gateway")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"{self.get_status_display()} payment {self.transaction_id or self.id} for order #{self.order.id}"

    @property
    def is_successful(self):
        if not self.status == self.PaymentStatus.SUCCESSFUL:
            self.status = self.PaymentStatus.SUCCESSFUL
            self.save()
        return self.status