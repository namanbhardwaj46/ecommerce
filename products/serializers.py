from rest_framework import serializers

from products.models import Products, Category, Orders, OrderItems


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = '__all__' #('id', 'name', 'description')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Orders
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = '__all__'

