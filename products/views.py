from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render
from pyexpat.errors import messages
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product, Category
from products.serializers import ProductSerializer, CategorySerializer
# from products.services import OrderCalculator
from django.db.models import Q


# Create your views here.

def hello(request):
    data = Product.objects.all()
    data = data[0]
    print(data.name)
    data.name = "ABC"
    data.save()
    data = Product.objects.get(id=1)
    print(data.name)
    return HttpResponse('Hello World!')


# noinspection PyInconsistentReturns
@api_view(['GET', 'POST'])
def create_or_get_products(request):
    if request.method == 'GET':
        # Fetch all products from database.
        data = Product.objects.all()
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
        data = Product.objects.get(id=id)
        # print(data)
        # Serialize the fetched data into a format suitable for JSON response.
        serializedProducts = ProductSerializer(data)
        # Return the serialized data as an API response.
        return Response(serializedProducts.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
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
    filtered_products = Product.objects.filter(filter_query)

    # Serialize the filtered products and convert them into JSON-friendly format
    serialized_results = ProductSerializer(filtered_products, many=True).data
    
    # Return response with metadata
    return Response({
        'count': len(serialized_results),
        'results': serialized_results
    }, status=status.HTTP_200_OK)


# noinspection PyInconsistentReturns
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

                # ** operator is used to unpack a dictionary into keyword arguments. When you use
                # {**category_serializer.data, "message": "Category created successfully!"}, you are merging two
                # dictionaries: category_serializer.data and {"message": "Category created successfully!"}.
                return Response({**category_serializer.data, "message": "Category created successfully!"},
                                status=status.HTTP_201_CREATED) # Success response
            return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST) # Error response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Error response


#PATCH allows partial updates without affecting others, and also can update fully.
@api_view(['PATCH'])
def update_product(request, id):
    try:
        product = Product.objects.get(id=id)  # Get the product
        serialized_product = ProductSerializer(product, data=request.data, partial=True)  # Allow partial updates

        if serialized_product.is_valid():
            serialized_product.save()  # Save changes
            return Response(serialized_product.data, status=status.HTTP_200_OK)

        return Response(serialized_product.errors, status=status.HTTP_400_BAD_REQUEST)

    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


