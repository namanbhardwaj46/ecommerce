from decimal import Decimal


class OrderCalculator:
    """Service class for handling complex order calculations"""
    @classmethod
    def calculate_order_total(cls, order, full_save=False):
        """
        Calculate all financial aspects of an order:
        1. Calculate subtotal from line items
        2. Apply absolute discount
        3. Calculate taxes
        4. Add shipping costs
        5. Calculate final total
        6. full_save: Whether to perform a full save on the order model.
                          If False, only updates specific fields and saves them separately.
                          This can improve performance when updating multiple orders at once.
                          Defaults to False.
        """
        # Calculate base subtotal
        order.subtotal = sum(item.line_total for item in order.order_items.all())

        # Apply absolute discount (cannot make subtotal negative)
        order.subtotal = max(order.subtotal - order.discount, Decimal('0.00'))

        # Calculate tax amount
        tax_amount = order.subtotal * (order.tax_rate / Decimal('100.00'))

        # Calculate total with shipping
        order.total = order.subtotal + tax_amount + order.shipping_cost

        ## Save the calculated values

        if full_save or not order.pk:
            # New instance or explicit full save
            order.save()
        else:
            # Optimized partial update
            order.save(['subtotal', 'total', 'updated_at'])
        return order