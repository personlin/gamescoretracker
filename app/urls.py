from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('players/', views.player_list, name='player_list'),
    path('players/create/', views.create_player, name='create_player'),
    path('players/edit/<int:player_id>/', views.edit_player, name='edit_player'),
    path('games/', views.game_list, name='game_list'),
    path('games/create/', views.create_game, name='create_game'),
    path('games/<int:game_id>/', views.game_detail, name='game_detail'),
    path('games/<int:game_id>/edit/', views.edit_game, name='edit_game'),
    path('games/<int:game_id>/export/', views.export_to_sheets, name='export_to_sheets'),
    path('games/<int:game_id>/update_score/<int:player_id>/<str:action>/', views.update_score, name='update_score'),
    path('games/<int:game_id>/score_records/', views.score_records, name='score_records'),
    path('score_records/<int:record_id>/edit/', views.edit_score_record, name='edit_score_record'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
