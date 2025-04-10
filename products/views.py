from django.core.serializers import serialize
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from products.models import Products
from products.serializers import ProductSerializer


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
        try:
            # Fetch all products from database.
            data = Products.objects.all()
            # Serialize the fetched data for JSON response.
            serializedProducts = ProductSerializer(data, many=True)
            return Response(serializedProducts.data) # Return the serialized data in a successful response.
        except Products.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    elif request.method == 'POST':
        try:
            # Deserialize and validate the incoming data.
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                # Save the valid data into the database.
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED) # Success response
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) # Error response
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # Error response


@api_view(['GET'])
def get_product(request, id):
    try:
        # Fetch product with given ID from database.
        data = Products.objects.get(id=id)
        print(data)
        # Serialize the fetched data into a format suitable for JSON response.
        serializedProducts = ProductSerializer(data)
        # Return the serialized data as an API response.
        return Response(serializedProducts.data)
    except Products.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND) # Requested product with given ID does not exist.



# GET:

# /product/1 -> return me data

# DELETE
# /product/1 -> delete data...


# TODO:  CREATE AN API FOR CREATING AND SAVING PRODUCT TO DATABASE...
