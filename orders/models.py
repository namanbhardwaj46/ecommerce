from django.utils import timezone  # Provides timezone-aware datetime objects
from decimal import Decimal
from django.core.exceptions import ValidationError  # Allows raising errors for invalid data
from django.db import models
from users.models import User
from products.models import Product
from utils.mixins import AuditableMixin
from django.db import transaction  # Enables atomic transactions to ensure data consistency


# Create your models here.

class Order(AuditableMixin):
    """Main order model handling transaction details"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, through='OrderProduct', related_name='orders')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Track total amount of an order.
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Paid Amount",
                                      help_text="Total amount paid towards this order")

    class OrderStatus(models.TextChoices):
        """
        Enumeration of all possible order states with descriptive labels.
        Defines the complete lifecycle of an order.
        """
        PENDING = 'pending', 'Pending Confirmation'  # Waiting for customer confirmation
        CONFIRMED = 'confirmed', 'Confirmed'  # Order is confirmed and ready for processing
        PARTIAL = 'partial', 'Partially Paid'  # Added for partial payments
        PAID = 'paid', 'Fully Paid'  # Explicitly track paid orders
        DELIVERED = 'delivered', 'Delivered'  # Order has been successfully delivered
        CANCELLED = 'cancelled', 'Cancelled'  # Order was cancelled
        RETURNED = 'returned', 'Returned'  # Order was returned by the customer

    # Class-level constants
    TERMINAL_STATUSES = [
        OrderStatus.DELIVERED,  # Final state: Order delivered successfully
        OrderStatus.CANCELLED,  # Final state: Order cancelled
        OrderStatus.RETURNED  # Final state: Order returned
    ]

    status = models.CharField(max_length=15, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completed At",
                help_text="Date and time when the order was fully paid / When order reached terminal status.")

    class Meta:
        # indexes = [
        #     models.Index(fields=['status']),  # Optimizes queries by status
        #     models.Index(fields=['user', 'created_at']),  # Optimizes user-specific order queries
        #     models.Index(fields=['created_at']),  # Optimizes queries by creation time
        # ]
        ordering = ['-created_at']  # Default ordering by newest first
        verbose_name = "Order"  # Singular name for the admin panel
        verbose_name_plural = "Orders"  # Plural name for the admin panel


    def clean(self):
        """
        Validate the order meets all business rules before saving.
        Called automatically during model validation.
        """
        # Business Rule 1: Every order must contain at least one product
        if self.pk and not self.order_items.exists():  # If it's an existing instance and there are no order items
            # Validation error if the order has no associated products
            raise ValidationError("An order must have at least one product.")

        # Business Rule 2: Ensure the discount does not exceed the subtotal
        if self.discount > self.subtotal:
            raise ValidationError({
                'discount': "Discount cannot exceed order subtotal."
            })

        # Business Rule 3: Validate valid status transitions for updates only
        if self.pk: # If the order exists in the database
            # Fetch the current order instance from the database
            original = Order.objects.get(pk=self.pk)  # Fetch the original order from DB
            # Ensure the status transition is allowed
            self.validate_status_transition(original)

    def validate_status_transition(self, original):
        """
        Internal method to validate status changes.
        Prevents invalid workflow transitions and ensures order validity.
        """
        # Rule 1: Prevent changes from terminal states
        if (original.status in self.TERMINAL_STATUSES and   # Original status is terminal
            self.status != original.status):  # New status differs from terminal status
            raise ValidationError(f"Cannot change status from {original.get_status_display()}"
            )

        # Rule 2: Ensure terminal statuses require at least one product
        if self.status in self.TERMINAL_STATUSES and not self.order_items.exists():
            # Raise an error if the order has no products and is set to terminal status
            raise ValidationError(
                "Orders marked as delivered, returned, or cancelled must include at least one product.")

    def save(self, *args, **kwargs):
        """
        Custom save handler with:
        - Atomic transactions for data integrity
        - Status tracking
        - Automatic total calculation
        """
        with transaction.atomic():  # Ensure atomicity across multiple operations /
                                    # Ensures all database operations are atomic
            # Handle terminal state transitions
            if self.pk:  # If the order already exists in the database (updating)
                # Fetch the original order from the database
                original = Order.objects.get(pk=self.pk)
                if self.status in self.TERMINAL_STATUSES: # If new status is terminal
                    if original.status not in self.TERMINAL_STATUSES: # If original was non-terminal
                        self.completed_at = timezone.now()  # Set the completion timestamp
                else: # If the new status is non-terminal
                    self.completed_at = None    # Reset the completion timestamp

            # Handle order creation (no primary key yet)
            if not self.pk:
                super().save(*args, **kwargs)  # Save the initial record to generate a primary key
                self.calculate_totals()  # Calculate totals after creation
                return super().save(    # Save again to store the calculated fields
                    update_fields=['subtotal', 'total', 'completed_at'] # Only update specific fields
                )

            # For updates: Recalculate totals and save the updated record
            self.calculate_totals()  # Recalculate totals for financial fields
            super().save(*args, **kwargs)  # Save the record

    def calculate_totals(self):
        """
        Recalculate all financial fields:
        - Subtotal from order items
        - Total with all adjustments
        Ensures totals are never negative.
        """
        # Calculate subtotal for this order as the sum of line totals (quantity × price_at_time)
        self.subtotal = sum(
            item.line_total() for item in
            self.order_items.select_related('product').all() # Prefetch related all products of this order for efficiency
            ) if hasattr(self, 'order_items') else Decimal('0') # Default to 0 if no products

        # Calculate the total amount, ensuring no negative totals
        # Convert all values to Decimal to ensure consistent types
        self.total = max(
            (self.subtotal - Decimal(str(self.discount))) + Decimal(str(self.shipping_cost)) + Decimal(str(self.tax_rate)),   # Total formula
            Decimal('0')    # Prevents negative values
        )

    def get_product_quantities(self):
        """
        Get list of products and their quantities in this order.
        Returns:
            list: of (product, quantity) tuples
        """
        return [
            (item.product, item.quantity)   # Create a tuple of product and quantity
            for item in self.order_items.select_related('product').all()    # Prefetch related products
        ]

    def __str__(self):
        """Human-readable representation of the order"""
        return f"Order #{self.id} ({self.get_status_display()}) - ₹{self.total:.2f}" #rounding upto two decimals


class OrderProduct(AuditableMixin):
    """Through model for product-order relationship with pricing details"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1) # Ensure every order item has at least 1 product. Track product quantity.
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the product when ordered

    class Meta:
        unique_together = ('order', 'product')  # Ensures each product is listed only once per order
        verbose_name = 'Order Item' # Singular name for the admin interface
        verbose_name_plural = 'Order Items' # Plural name for the admin interface

    def clean(self):
        """
        Validate the line item meets business rules.
        """
        # Validate sufficient stock
        if hasattr(self, 'product') and self.quantity > self.product.stock_quantity:
            raise ValidationError({'quantity': f"Only {self.product.stock_quantity} units are available."})


    def save(self, *args, **kwargs):
        """
        Custom save handler that:
        1. Validates the line item
        2. Captures current product price on creation
        3. Updates parent order totals
        """
        self.full_clean()  # Ensure validation runs before saving

        # First save - capture current price
        if not self.pk:  # Check if this is the first time saving the line item
            self.price_at_time = self.product.price  # Freeze the product price at purchase

        super().save(*args, **kwargs)  # Perform the actual save operation

        # Update parent order totals
        self.order.calculate_totals()  # Recalculate the parent order totals
        self.order.save()  # Save the updated parent order

    def line_total(self):
        """
        Calculate the total price for this line item.
        Returns:
            Decimal: quantity × price_at_time
        """
        return self.quantity * self.price_at_time   # Multiply quantity by the frozen price

    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ ₹{self.price_at_time:.2f} in Order #{self.order.id}"