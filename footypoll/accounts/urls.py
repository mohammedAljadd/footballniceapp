from django.urls import path
from .views import signup_view, CustomLoginView, custom_logout_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout_view, name='logout'),
]