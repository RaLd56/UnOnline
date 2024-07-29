
from django.urls import path
from . import views

urlpatterns = [
    path('start_game/', views.start_game, name='start_game'),
    path('create_room/', views.create_room, name='create_room'),
    path('join_room/', views.join_room, name='join_room'),
    path('game_room/<str:room_name>/', views.game_room, name='game_room'),
    path('game/<str:room_name>/play_card/<int:card_id>/', views.play_card, name='play_card'),
    path('game/<str:room_name>/get_extra_card/', views.get_extra_card, name='get_extra_card'),
    path('room/<str:room_name>/choose_color/', views.choose_color, name='choose_color'),
    path('room/<str:room_name>/uno/', views.uno, name='uno'),
    path('update-room-data/<str:room_name>/', views.update_room_data, name='update_room_data'),
]


