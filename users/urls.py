from django.urls import path
from .views import CreateListUserView, UserDetailView

urlpatterns = [
    # List all users or create a new user endpoint.
	path('', CreateListUserView.as_view(), name='user-list'),
    # Retrieve, update or delete an existing user endpoint.
	path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]