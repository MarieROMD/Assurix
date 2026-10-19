
"""
URL configuration for assurix project.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "connexion/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),

    path(
        "deconnexion/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("", include("core.urls")),
]