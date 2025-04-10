from django.urls import path

# from ecommerce.urls import urlpatterns
from products import views

urlpatterns = [
    # Maps the 'hello' view, which could be an introductory or test endpoint
    path('hello/', views.hello),
    # Maps the 'create_or_get_products' view, which returns all products or can create new products and save.
    path('Products/', views.create_or_get_products),
    path('product/<int:id>/', views.get_product),
]