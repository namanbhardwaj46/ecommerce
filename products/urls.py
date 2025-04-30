from django.urls import path

# from ecommerce.urls import urlpatterns
from products import views
from products.views import CreateListOrderView, DetailOrderView

urlpatterns = [
    # Maps the 'hello' view, which could be an introductory or test endpoint
    path('hello/', views.hello),
    # Maps the 'create_or_get_products' view, which returns all products or can create new products and save.
    path('products/', views.create_or_get_products),
    # Maps the 'get_product' view, which returns a single product by ID.
    path('product/<int:id>/', views.get_product, name="get_product"),
    # Maps the 'filter_product' view, which filters products based on query parameters.
    path('filter-products/', views.filter_products, name="filter_products"),
    # Maps the 'create_category' view, which creates a new category and saves it to the database.
    path('categories/', views.create_or_get_category, name="create_or_get_category"),
    path('orders/', CreateListOrderView.as_view(), name="create-list-order"), # Creates or lists orders. (Class Based View)
    path('orders/<int:pk>', DetailOrderView.as_view(), name="detail-order") # Gets, updates, or deletes a specific order. (Class Based View)

]