
from django.urls import path
from . import views

urlpatterns = [
    path('start_game/', views.start_game, name='start_game'),
    path('create_room/', views.create_room, name='create_room'),
    path('join_room/', views.join_room, name='join_room'),
    path('game_room/<str:room_name>/', views.game_room, name='game_room'),
    path('game/<str:room_name>/play_card/<int:card_id>/', views.play_card, name='play_card'),
    path('game/<str:room_name>/get_extra_card/', views.get_extra_card, name='get_extra_card')
]



'''from django.urls import path, include
from . import views

urlpatterns = [
    path('startgame/', views.startgame, name='startgame'),
    path('create_room/', views.create_room, name='createroom'),
    path('join_room/', views.join_room, name='join_room'),
    path('room/<str:room_name>/', views.room, name='room'),
]'''