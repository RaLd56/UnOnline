
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GameRoom, Card, PlayerCard
from .forms import GameRoomForm, JoinRoomForm
from .utils import deal_cards
from django.http import HttpResponseForbidden


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
            return redirect('game_room', room_name=room.name)
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
                return render(request, 'game/room_full.html')
            room.add_player(request.user)
            if room.players.count() == 2:  # Начинаем игру, когда 2 игрока
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

    # Извлекаем карты текущего игрока
    current_player_hand = room.player_cards.filter(player=request.user)
    
    # Извлекаем карты других игроков
    player_info = []
    for player in room.players.all():
        if player != request.user:
            player_hand = room.player_cards.filter(player=player)
            player_info.append({
                'player': player,
                'cards': player_hand
            })

    context = {
        'room': room,
        'current_player_hand': current_player_hand,
        'player_info': player_info,
    }

    return render(request, 'game/game_room.html', context)

@login_required
def play_card(request, room_name, card_id):
    room = get_object_or_404(GameRoom, name=room_name)
    
    # Проверяем, что текущий пользователь участвует в игре
    if request.user not in room.players.all():
        return redirect('start_game')
    
    card = get_object_or_404(Card, id=card_id)
    player_card = get_object_or_404(PlayerCard, player=request.user, card=card, room=room)

    # Получаем последнюю сыгранную карту
    last_played_card = room.last_played_card

    # Проверяем, можно ли сыграть карту
    if last_played_card:
        # Если карта специальная, она может быть сыграна в любом случае
        if card.suit == last_played_card.suit or card.type == last_played_card.type or card.suit == 'S':
            # Обновляем последнюю сыгранную карту
            room.last_played_card = card
            room.save()
            
            # Удаляем карту из руки игрока
            player_card.delete()
            
            # Обрабатываем действие специальных карт
            handle_special_card(room, card)
            
            return redirect('game_room', room_name=room_name)
        else:
            return HttpResponseForbidden("You cannot play this card.")
    else:
        # Если нет последней сыгранной карты, любой ход возможен (может быть специальное условие)
        room.last_played_card = card
        room.save()
        player_card.delete()
        handle_special_card(room, card)
        return redirect('game_room', room_name=room_name)

def handle_special_card(room, card):
    # Обработка действий специальных карт
    if card.type == 'wild':
        # Пример: если карта - дикая, можно попросить игрока выбрать цвет
        pass
    elif card.type == 'wild_draw_4':
        # Пример: если карта - дикая + 4, следует добавить 4 карты к руке следующего игрока
        pass
    elif card.type == 'skip':
        # Пример: если карта - пропуск, следующий игрок пропускает ход
        pass
    elif card.type == 'reverse':
        # Пример: если карта - реверс, меняем порядок хода
        pass
    elif card.type == 'draw_2':
        # Пример: если карта - взять 2, следующий игрок берет 2 карты
        pass


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
