from django.urls import path

# from ecommerce.urls import urlpatterns
from products import views

urlpatterns = [
    # Maps the 'hello' view, which could be an introductory or test endpoint
    path('hello/', views.hello),
    # Maps the 'create_or_get_products' view, which returns all products or can create new products and save.
    path('Products/', views.create_or_get_products),
    # Maps the 'get_product' view, which returns a single product by ID.
    path('product/<int:id>/', views.get_product),
    # Maps the 'filter_product' view, which filters products based on query parameters.
    path('filter-products/', views.filter_products),
    # Maps the 'create_category' view, which creates a new category and saves it to the database.
    path('create-category/', views.create_category),
]