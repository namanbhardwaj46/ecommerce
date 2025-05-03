from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import Order
from .serializers import OrderSerializer

# Create your views here.

# Class based Orders Views

# View to create orders or get all orders.
class CreateListOrderView(APIView):
    """
    Endpoint for listing orders and creating new orders
    """
    def get(self, request):
        # Fetch all orders from the database with related products.
        data = Order.objects.prefetch_related('order_items').all()
        # Serialize the fetched data for JSON response.
        order_serializer = OrderSerializer(data, many=True)
        return Response(order_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            # Create a new order with request data.
            order_serializer = OrderSerializer(data=request.data)
            if order_serializer.is_valid():
                order_serializer.save()
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View to retrieve, update, or delete a specific order.
class OrderDetailView(APIView):
    def get_object(self, pk):
        # Helper method to retrieve an order object by its primary key (pk).
        try:
            return Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return None
    def get(self, request, pk):
        # Retrieve details of a specific order.
        order = self.get_object(pk)
        if not order:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        # Update details of a specific order partially or fully.
        order = self.get_object(pk)
        if not order:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order, data=request.data, partial=True) # Partially update the order.
        if serializer.is_valid():
            serializer.save() # Save the updated order.
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        # Delete a specific order.
        order = self.get_object(pk)
        if not order:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
