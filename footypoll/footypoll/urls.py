"""
URL configuration for footypoll project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('matches.urls')),
    path('accounts/', include('accounts.urls')),  # your custom auth views
    # Remove the duplicate django.contrib.auth.urls line since you're handling auth in accounts.urls
]