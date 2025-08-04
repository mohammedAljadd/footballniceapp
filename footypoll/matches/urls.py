from django.urls import path
from . import views

urlpatterns = [
    path('', views.match_list, name='match_list'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    path('match/<int:match_id>/toggle/', views.toggle_participation, name='toggle_participation'),
    path('logs/', views.action_log, name='action_log'),  # new logs page
]
