"""scinguistics_archive URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path

# Use include() to add paths from applications
from django.urls import include

# Use RedirectView() to redirect the base url to an application
from django.views.generic import RedirectView

# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    # applications
    path("catalog/", include("catalog.urls")),
    # redirections
    path("", RedirectView.as_view(url="catalog/", permanent=True)),
    # static files
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
    # authentication (auth.urls needed for 'LOGOUT_REDIRECT_URL' in settings.py to work properly, used in 'base_generic.html for url logout)
    path("accounts/", include("django.contrib.auth.urls")),
    # django-allauth - for patreon authentication
    path("accounts/", include("allauth.urls")),
    # backblaze b2
    path("", include("django_backblaze_b2.urls")),
]
