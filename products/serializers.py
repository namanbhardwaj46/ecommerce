from rest_framework import serializers

from products.models import Products, Category, Orders, OrderProduct


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


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = '__all__'

