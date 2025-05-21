from rest_framework.exceptions import ValidationError  # Handles validation errors raised by serializers.
from rest_framework.views import APIView  # Base class for creating class-based views in Django REST Framework.
from rest_framework.response import Response  # Used for creating HTTP responses with JSON data.
from rest_framework import status  # Provides HTTP status codes like 200, 400, 404, etc.
from django.db import transaction   # Provides atomic transactions to ensure consistent database updates.
from django.http import Http404 # Exception class for raising "Not Found" errors.
from .models import Order   # Imports the Order model representing customer orders.
from .serializers import OrderSerializer    # Imports the serializer for handling Order data.
from .services import OrderService  # Imports service layer encapsulating business logic.
from .exceptions import OrderValidationError  # Imports custom exception for validation-specific errors.
from products.models import Product  # Imports the Products model for fetching product details.
import logging  # Used to log information, warnings, and errors for debugging.


logger = logging.getLogger(__name__) # Configures a logger instance for logging output in this module.


class CreateListOrderView(APIView):
    """
    API view to handle listing and creating orders.

    This class provides two main functionalities:
    - Listing all orders with optimized database queries.
    - Creating a new order with atomic transaction handling.

    Methods:
        get_queryset: Fetches all orders with preloaded related data.
        get: Handles GET requests to retrieve a list of all orders.
        post: Handles POST requests to create a new order.
    """

    def get_queryset(self):
        """
        Fetch all orders from the database with optimized queries.
        - `prefetch_related`: Preloads related products for each order to minimize database hits.
        - `select_related`: Preloads user information in a single query to improve performance.
        """
        return Order.objects.prefetch_related('order_items__product').select_related('user')

    def get(self, request):
        """
        Handles GET requests to retrieve a list of all orders.
        - Fetches the optimized queryset.
        - Serializes the queryset into JSON data.
        - Returns the serialized data in an HTTP response.
        """
        queryset = self.get_queryset() # Fetch all orders with preloaded relationships.
        # Serialize the fetched data for JSON response.
        order_serializer = OrderSerializer(queryset, many=True) # Serialize multiple orders into JSON format.
        return Response(order_serializer.data, status=status.HTTP_200_OK) # Return serialized data with HTTP 200 status.

    @transaction.atomic
    def post(self, request):
        """
        Handles POST requests to create a new order.
        - Wraps creation logic in an atomic transaction to prevent partial saves on failure.
        """
        try:
            order_serializer = OrderSerializer(data=request.data)   # Deserialize request data for order creation.
            order_serializer.is_valid(raise_exception=True)  # Validate the input data and raise errors if invalid.
            order = order_serializer.save() # Save the validated data into the database as a new Order object.
            logger.info(f"Order {order.id} created successfully")  # Log the success message.
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)  # Return created order with HTTP 201.
        except Exception as e:
            logger.error(f"Order creation failed: {str(e)}", exc_info=True)  # Log the error message and traceback.
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)  # Return error with HTTP 400.


class OrderDetailView(APIView):
    """
    API view to handls detailed operations for a single order.

    This class provides functionalities to:
    - Retrieve the details of a specific order.
    - Update the details of a specific order, either partially or fully.
    - Delete a specific order.

    Methods:
        get_object: Helper method to retrieve an order by its primary key.
        - Uses `select_related` to optimize user data retrieval.
        - Uses `prefetch_related` to optimize product data retrieval for the order.
        get: Handles GET requests to retrieve order details.
        patch: Handles PATCH requests to update order details.
        - Allows partial updates.
        - Uses atomic transactions to ensure consistent updates.
        delete: Handles DELETE requests to remove an order.
    """

    def get_object(self, pk):
        try:
            return Order.objects.select_related('user').prefetch_related('order_items__product') \
                    .get(pk=pk) # Fetch the order by primary key.
        except Order.DoesNotExist:
            raise Http404("Order not found.") # Raise a 404 error if the order is not found.

    def get(self, request, pk):
        order = self.get_object(pk) # Fetch the order or raise a 404 if not found.
        return Response(OrderSerializer(order).data)    # Serialize and return the order data in the response.

    @transaction.atomic
    def patch(self, request, pk):
        order = self.get_object(pk) # Fetch the order or raise a 404 if not found.
        try:
            serializer = OrderSerializer(order, data=request.data, partial=True) # Deserialize data for partial updates.
            serializer.is_valid(raise_exception=True) # Validate the input data and raise errors if invalid.

            self._process_order_update(order, request.data) # Process any necessary business logic before saving.
                                                            # Handle updates for status, products, or other fields.
            OrderService.calculate_order_totals(order) # Recalculate totals for the updated order.

            return Response(OrderSerializer(order).data) # Serialize and return the updated order data.
        except OrderValidationError as e:
            logger.warning(f"Order validation failed: {str(e)}") # Log validation error.
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST) # Return error with HTTP 400.
        except Product.DoesNotExist as e:
            logger.error(f"Invalid product ID: {str(e)}")   # Log invalid product error.
            return Response({'error': 'Invalid product ID.'}, status=status.HTTP_400_BAD_REQUEST) # Return error for invalid product.
        except Exception as e:
            logger.error(f"Order update failed: {str(e)}", exc_info=True) # Log unexpected error.
            return Response({'error': f'Update failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST) # Return generic error response.

    def delete(self, request, pk):
        # Delete a specific order.
        order = self.get_object(pk) # Fetch the order or raise a 404 if not found.
        try:
            order.delete()  # Delete the order from the database.
            return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)  # Return HTTP 204 on successful deletion.
        except Exception as e:
            logger.error(f"Order deletion failed: {str(e)}", exc_info=True) # Log unexpected deletion error.
            return Response({'error': 'Deletion failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    # Return error with HTTP 500.

    # Helper Methods ::::: ::::::Handles specific update logic for orders and products.
    def _process_order_update(self, order, update_data):
        """
        Processes updates for the order atomically.
        Handles status updates, product updates, and direct field changes.
        """
        try:
            # Update order status
            if 'status' in update_data:
                OrderService.update_order_status(order, update_data['status'])  # Update status using service layer.

            # Update order items
            if 'order_items' in update_data:
                self._handle_products_update(order, update_data[
                    'order_items'])  # Delegate product updates to helper method.

            # Update other fields directly
            updatable_fields = ['discount', 'tax_rate', 'shipping_cost']    # Define which fields can be updated.
            for field in updatable_fields:
                if field in update_data:
                    setattr(order, field, update_data[field]) # Set attribute value based on provided data.
                                                              # Update field value on the order instance.

            order.full_clean()  # Validate the order instance after updates.
            order.save()  # Save the updated order to the database.

        except KeyError as e:
            raise OrderValidationError(f"Missing required field {str(e)}") # Raise error for missing fields.
        except ValidationError as e:
            raise OrderValidationError(str(e)) # Raise validation error for invalid data.

    def _handle_products_update(self, order, products_data):
        """
        Handles validation and updates for order products.
        """
        try:
            validated_products = [] # List to hold validated product data.
            for product_data in products_data:
                if 'product_id' not in product_data or 'quantity' not in product_data:
                    raise OrderValidationError(
                        "Product data requires both 'product_id' and 'quantity'."
                    )   # Validate required fields.

                product = Product.objects.get(pk=product_data['product_id'])    # Fetch product by ID.
                if product_data['quantity'] <= 0:
                    raise OrderValidationError(
                        "Quantity must be positive."
                    )   # Validate quantity.

                validated_products.append({
                    'product': product,
                    'quantity': product_data['quantity']
                })  # Append validated product to the list.

            OrderService.add_product_to_order(order, validated_products) # Add/update products using service layer.
        except Product.DoesNotExist:
            raise OrderValidationError("One or more products do not exist.") # Raise error if a product doesn't exist.
