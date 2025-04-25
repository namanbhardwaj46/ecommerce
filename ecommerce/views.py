from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view



@api_view(['GET'])
def health(request):
    return HttpResponse("OK", status=status.HTTP_200_OK)

