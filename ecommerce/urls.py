"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.urls import auth_urlpatterns, user_urlpatterns

urlpatterns = [
       path('admin/', admin.site.urls),

       # Customer authentication - SimpleJWT
       path("api/auth/", include(auth_urlpatterns)),

       # OAuth2 Authorization Server - Django OAuth Toolkit
       path("o/", include("oauth2_provider.urls", namespace="oauth2_provider")),
       path('api/products/', include('products.urls')),
       path("api/orders/", include('orders.urls')),
       path("api/users/", include(user_urlpatterns)),
      path("api/payments/", include('payments.urls')),

]
