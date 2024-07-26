
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GameRoom
from .forms import GameRoomForm, JoinRoomForm
from .utils import deal_cards

@login_required
def start_game(request):
    return render(request, 'game/start_game.html')

@login_required
def create_room(request):
    if request.method == 'POST':
        form = GameRoomForm(request.POST)
        if form.is_valid():
            room = form.save()
            room.add_player(request.user)
            return redirect('game_room', room_name=room.name)  # Перенаправление по имени комнаты
    else:
        form = GameRoomForm()
    return render(request, 'game/create_room.html', {'form': form})

@login_required
def join_room(request):
    if request.method == 'POST':
        form = JoinRoomForm(request.POST)
        if form.is_valid():
            room_name = form.cleaned_data['room_name']
            room = get_object_or_404(GameRoom, name=room_name)
            if room.is_full:
                return render(request, 'room_full.html')
            room.add_player(request.user)
            if room.players.count() == 2:  # Предположим, что нужно 2 игрока для начала
                player_hands = deal_cards(room)
                request.session['player_hands'] = player_hands
            return redirect('game_room', room_name=room.name)
    else:
        form = JoinRoomForm()
    return render(request, 'game/join_room.html', {'form': form})

@login_required
def game_room(request, room_name):
    room = get_object_or_404(GameRoom, name=room_name)
    if request.user not in room.players.all():
        return redirect('start_game')

    player_hands = request.session.get('player_hands', {})
    
    # Получаем карты текущего игрока и других игроков
    current_player_hand = player_hands.get(request.user, [])
    player_info = []
    for player in room.players.all():
        if player != request.user:
            player_info.append({
                'player': player,
                'cards': player_hands.get(player, [])
            })

    context = {
        'room': room,
        'current_player_hand': current_player_hand,
        'player_info': player_info,
    }
    return render(request, 'game/game_room.html', context)



'''from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Player, Card
from .forms import RoomCreationForm, JoinRoomForm
from .utils import deal_cards

@login_required
def startgame(request):
    return render(request, 'game/startgame.html')

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomCreationForm(request.POST)
        if form.is_valid():
            room = form.save()
            Player.objects.create(user=request.user, room=room)
            return redirect('room', room_name=room.name)
    else:
        form = RoomCreationForm()
    return render(request, 'game/create_room.html', {'form': form})

@login_required
def join_room(request):
    if request.method == 'POST':
        form = JoinRoomForm(request.POST)
        if form.is_valid():
            room_name = form.cleaned_data['room_name']
            room_password = form.cleaned_data['room_password']
            try:
                room = Room.objects.get(name=room_name, room_password=room_password)
                if room.players.count() < 2:
                    Player.objects.get_or_create(user=request.user, room=room)
                    return redirect('room', room_name=room.name)
                else:
                    messages.error(request, "Room is full.")
            except Room.DoesNotExist:
                messages.error(request, "Room not found or incorrect password.")
    else:
        form = JoinRoomForm()
    return render(request, 'game/join_room.html', {'form': form})

@login_required
def room(request, room_name):
    room = get_object_or_404(Room, name=room_name)
    players = room.players.all()
    current_player = get_object_or_404(Player, user=request.user, room=room)
    player_info = [{'player': player, 'cards': player.hand.all()} for player in players]

    # Check if cards need to be dealt
    if room.players.count() == 2 and not any(player.hand.exists() for player in players):
        deal_cards(room)

    return render(request, 'game/room.html', {'room': room, 'player_info': player_info, 'current_player': current_player})'''
