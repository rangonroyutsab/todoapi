from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


BASE_URL = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{BASE_URL}login/", TokenObtainPairView.as_view(), name="login"),
    path(f"{BASE_URL}token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(f"{BASE_URL}", include("users.urls")),
    path(f"{BASE_URL}", include("tasks.urls")),
]
