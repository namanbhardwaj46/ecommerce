from rest_framework import serializers
from orders.models import Order
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):   # Serializer to convert Payment model into JSON format
    order = serializers.PrimaryKeyRelatedField( # Primary key related field for the order
        queryset=Order.objects.all(),  # Ensures only valid Order IDs can be referenced
        help_text="Existing Order ID" # For better description look documentation in API views
    )


    class Meta:
        model = Payment # Link serializer to the Payment model
        fields = [  # Define the fields to be serialized
            'id', 'order', 'amount', 'currency', 'status', 'method', 'transaction_id', 'gateway', 'created_at']

        read_only_fields = [    # These fields should not be editable by the client
            'id', 'status', 'transaction_id', 'created_at'] #amount


    def validate_order(self, value):
        """
        Validation: Ensures the order is in a payable state before allowing payment processing.
        - Only orders in 'pending' or 'partial' status can have payments created.
        - Raises an error if the order is not eligible for payment.
        """
        if value.status not in [Order.OrderStatus.PENDING, Order.OrderStatus.PARTIAL]: # Use correct enum values here.
            raise serializers.ValidationError(
                "Only orders with pending or partial status will process payments."
            )
        return value    # Return the validated order instance

    # Method to validate and process payment data before saving it.
    def validate_amount(self, value):
        """
        Validation: Ensures the payment amount does not exceed the remaining payable amount of the order.
        - Retrieves the order instance using the provided order ID.
        - Calculates the remaining balance for the order.
        - Raises an error if the payment exceeds the allowable amount.
        """
        order_id = self.initial_data.get('order')   # Get order ID from request data
        if order_id:
            try:
                order = Order.objects.get(pk=order_id)  # Retrieve Order instance from DB
            except Order.DoesNotExist:
                raise serializers.ValidationError("Invalid order ID.")  # Raise an error if the order doesn't exist.

            remaining_balance = order.total - order.paid_amount  # Calculate remaining balance of the order to be paid.
            if value > remaining_balance:  # Check payment does not exceed the allowed amount.
                raise serializers.ValidationError(f"The maximum allowed amount is {remaining_balance}.")
            elif value <= 0:
                raise serializers.ValidationError("Payment amount must be greater than zero.")
        return value  # If validation passes, return the validated amount.
