from rest_framework import serializers
from .models import Order, OrderProduct
from .services import OrderCalculator

class OrderProductSerializer(serializers.ModelSerializer):
    """Serializer for individual order items"""
    class Meta:
        model = OrderProduct
        fields = ["product", "quantity", "price_at_time", "line_total"]
        # fields = '__all__'
        read_only_fields = ['price_at_time', 'line_total']


# Constants for financial fields
FINANCIAL_FIELDS = {'discount', 'tax_rate', 'shipping_cost'}
class OrderSerializer(serializers.ModelSerializer):
    """Main order serializer with nested items and calculations"""
    order_items = OrderProductSerializer(many=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'order_items', 'products', 'subtotal', 'discount', 'tax_rate',
                  'shipping_cost', 'total', 'created_at']
        read_only_fields = ['subtotal', 'total', 'created_at']


    def create(self, validated_data):
        """Custom create method with calculation workflow"""
        order_items_data = validated_data.pop('order_items')

        # Create base order
        order = Orders.objects.create(**validated_data)

        # Create order items with price snapshots
        for item in order_items_data:
            OrderProduct.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price_at_time=item['product'].price, # Price at time of order
                )
        # Trigger calculations
        OrderCalculator.calculate_order_total(order)
        return order

    def update(self, instance, validated_data):
        """Hybrid update method combining item updates and service layer calculations"""
        # Update specific order items
        order_items_data = validated_data.pop('order_items', None)

        # Update the order fields
        instance = super().update(instance, validated_data)

        # Handle item updates through serializer
        if order_items_data is not None:
            self._update_order_items(instance, order_items_data)

        # Determine if recalculation is needed
        financial_fields_changed = any(field in validated_data for field in FINANCIAL_FIELDS)
        order_items_data_changed = order_items_data is not None

        # Trigger recalculation if needed
        if financial_fields_changed or order_items_data_changed:
            OrderCalculator.calculate_order_total(instance)

        return instance

    def _update_order_items(self, order, order_items_data):
        """Handles complex order item updates with error handling"""
        for item_data in order_items_data:
            try:
                # Get existing order item
                order_item = OrderProduct.objects.get(
                    order=order, product=item_data['product']
                )

                # Update quantity if provided
                if 'quantity' in item_data:
                    order_item.quantity = item_data['quantity']

                # Update price if provided (with validation)
                if 'price_at_time' in item_data:
                    order_item.price_at_time = item_data['price_at_time']

                # Save and auto-calculate line_total
                order_item.save()
            except OrderProduct.DoesNotExist:
                # Handle missing items based on business rules
                raise serializers.ValidationError(f"Product {item_data['product'].id} not found in this order.")
