from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

import products
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


@api_view(['GET'])
def get_products(request):
    data = Products.objects.all()
    serializedProducts = ProductSerializer(data, many=True)
    return Response(serializedProducts.data)


@api_view(['GET'])
def get_product(request, id):
    try:
        data = Products.objects.get(id=id)
        print(data)
        serializedProducts = ProductSerializer(data)
        return Response(serializedProducts.data)
    except Products.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# GET:

# /product/1 -> return me data

# DELTE
# /product/1 -> delete data...


# TODO:  CREATE AN API FOR CREATING AND SAVING PRODUCT TO DATABASE...
