
from django.urls import path
from . import views

urlpatterns = [
    path('start_game/', views.start_game, name='start_game'),
    path('create_room/', views.create_room, name='create_room'),
    path('join_room/', views.join_room, name='join_room'),
    path('game_room/<str:room_name>/', views.game_room, name='game_room'),
]



'''from django.urls import path, include
from . import views

urlpatterns = [
    path('startgame/', views.startgame, name='startgame'),
    path('create_room/', views.create_room, name='createroom'),
    path('join_room/', views.join_room, name='join_room'),
    path('room/<str:room_name>/', views.room, name='room'),
]'''