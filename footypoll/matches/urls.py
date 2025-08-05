from django.urls import path
from . import views

urlpatterns = [
    path('', views.match_list, name='match_list'),
    path('match/<int:match_id>/', views.match_detail, name='match_detail'),
    path('match/<int:match_id>/toggle/', views.toggle_participation, name='toggle_participation'),
    path('match/<int:match_id>/notes/', views.update_player_notes, name='update_player_notes'),
    path('match/<int:match_id>/pdf/', views.export_match_pdf, name='export_match_pdf'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('stats/', views.stats_page, name='stats_page'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    
    # Staff/Admin only URLs
    path('manage/', views.manage_matches, name='manage_matches'),
    path('create/', views.create_match, name='create_match'),
    path('match/<int:match_id>/edit/', views.edit_match, name='edit_match'),
    path('match/<int:match_id>/delete/', views.delete_match, name='delete_match'),
    path('logs/', views.action_log, name='action_log'),
]