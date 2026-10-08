from django.urls import path
from .views import UserSignUpView, UserDetailView, MeView, UserLoginView, ListUserView
from rest_framework_simplejwt.views import TokenBlacklistView, TokenRefreshView

# Authentication URLs
auth_urlpatterns  = [
	# Register a new user endpoint.
	path('register/', UserSignUpView.as_view(), name='user-register'),

	# Login a user endpoint.
	path("login/", UserLoginView.as_view(), name="user-login"),

	path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),

	path("logout/", TokenBlacklistView.as_view(), name="logout"),

    path("me/", MeView.as_view(), name="me"),

]

# User management URLs
user_urlpatterns = [
	# List all users or create a new user endpoint.
	path('', ListUserView.as_view(), name='user-list'),

	# Retrieve, update or delete an existing user endpoint.
	path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]