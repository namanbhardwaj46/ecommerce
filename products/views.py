from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Products, Orders, Category
from products.serializers import ProductSerializer, CategorySerializer, OrderSerializer
from django.db.models import Q


# Create your views here.

def hello(request):
    data = Products.objects.all()
    data = data[0]
    print(data.name)
    data.name = "ABC"
    data.save()
    data = Products.objects.get(id=1)
    print(data.name)
    return HttpResponse('Hello World!')


@api_view(['GET', 'POST'])
def create_or_get_products(request):
    if request.method == 'GET':
        # Fetch all products from database.
        data = Products.objects.all()
        # Serialize the fetched data for JSON response.
        serializedProducts = ProductSerializer(data, many=True)
        return Response(serializedProducts.data, status=status.HTTP_200_OK) # Return the serialized data in a successful response.

    elif request.method == 'POST':
        try:
            # Deserialize and validate the incoming data.
            product_serializer = ProductSerializer(data=request.data)
            if product_serializer.is_valid():
                # Save the valid data into the database.
                product_serializer.save()
                return Response(product_serializer.data, status=status.HTTP_201_CREATED) # Success response
            return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST) # Error response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Error response


@api_view(['GET'])
def get_product(request, id):
    try:
        # Fetch product with given ID from the database.
        data = Products.objects.get(id=id)
        print(data)
        # Serialize the fetched data into a format suitable for JSON response.
        serializedProducts = ProductSerializer(data)
        # Return the serialized data as an API response.
        return Response(serializedProducts.data, status=status.HTTP_200_OK)
    except Products.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND) # Requested product with given ID does not exist.



@api_view(['GET'])
def filter_products(request):
    """
    Filter products by name, description, and price range.
    Filtering products using AND conditions.
    Filtering products using OR conditions is not implemented yet.
    """
    # Validation errors container
    validation_errors = {}
    
    # Get filter parameters from query string
    # Extract 'name' and 'description' from query parameters
    name_query = request.GET.get('name', default=None)
    description_query = request.GET.get('description', default=None)

    # Adding validation checks for name to check name parameter cannot be empty
    if name_query is not None:
        if not name_query.strip() or name_query in ['""', "''", "None"]:
            validation_errors["name"] = "Product Name cannot be empty."
    # print(f"name: {repr(name_query)}", type(name_query))  # Use repr() to see if it's None or an empty string

    min_price = request.GET.get('min_price', default=None)
    max_price = request.GET.get('max_price', default=None)
    # available = request.GET.get('is_available', default=None)

    # Validate price parameters
    if min_price:
        try:
            min_price = float(min_price)
            if min_price < 0:
                validation_errors['min_price'] = "Price cannot be negative"
        except ValueError:
            validation_errors['min_price'] = "Must be a valid number"
    
    if max_price:
        try:
            max_price = float(max_price)
            if max_price < 0:
                validation_errors['max_price'] = "Price cannot be negative"
        except ValueError:
            validation_errors['max_price'] = "Must be a valid number"
    
    # Check if min_price is greater than max_price
    if min_price and max_price and float(min_price) > float(max_price):
        validation_errors['price_range'] = "Minimum price cannot be greater than maximum price"
    
    # If there are validation errors, return them
    if validation_errors:
        return Response(
            {"errors": validation_errors}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Initialize an empty filter using Q objects to dynamically combine conditions
    filter_query = Q()
    
    # Apply filters if parameters are provided
    if name_query:
        filter_query &= Q(name__icontains=name_query)

    # Apply filters if parameters are provided
    if description_query:
        filter_query &= Q(description__icontains=description_query)

    # Apply price range filters
    if min_price:
        filter_query &= Q(price__gte=min_price) # Products with price >= min_price
    
    if max_price:
        filter_query &= Q(price__lte=max_price) # Products with price <= max_price

    # Fetch products from the database that match the constructed filter query
    filtered_products = Products.objects.filter(filter_query)

    # Serialize the filtered products and convert them into JSON-friendly format
    serialized_results = ProductSerializer(filtered_products, many=True).data
    
    # Return response with metadata
    return Response({
        'count': len(serialized_results),
        'results': serialized_results
    }, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
def create_or_get_category(request):
    if request.method == "GET":
        # Fetch all categories from the database.
        data = Category.objects.all()
        # Serialize the fetched data for JSON response.
        category_serializer = CategorySerializer(data, many=True)
        return Response(category_serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        try:
            # Deserialize and validate the incoming data.
            category_serializer = CategorySerializer(data=request.data)
            if category_serializer.is_valid():
                # Save the valid data into the database.
                category_serializer.save()
                return Response(category_serializer.data, status=status.HTTP_201_CREATED) # Success response
            return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST) # Error response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Error response



# Class based Orders Views

# View to create orders or get all orders.
class CreateListOrderView(APIView):
    def get(self, request):
        # Fetch all orders from the database.
        data = Orders.objects.all()
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
class DetailOrderView(APIView):
    def get_object(self, pk):
        # Helper method to retrieve an order object by its primary key (pk).
        try:
            return Orders.objects.get(pk=pk)
        except Orders.DoesNotExist:
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