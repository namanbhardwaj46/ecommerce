from django.urls import path
from .views import CreateListOrderView, OrderDetailView

urlpatterns = [
	# List and create orders endpoint. (Class Based View)
	path('', CreateListOrderView.as_view(), name='create-list-orders'),
	# Retrieve, update or delete an existing order endpoint. (Class Based View)
	path('<int:pk>/', OrderDetailView.as_view(), name='order-detail')
]