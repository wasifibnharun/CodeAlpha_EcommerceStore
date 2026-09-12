from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from store import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/register/", views.register, name="register"),
    path("", include("store.urls")),
]
