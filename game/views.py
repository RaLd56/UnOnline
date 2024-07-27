from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GameRoom, Card, PlayerCard
from .forms import GameRoomForm, JoinRoomForm
from .utils import deal_cards
from django.http import HttpResponseForbidden
from django.contrib import messages


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
                deal_cards(room)
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
                'cards': player_hand,
                'turn': room.turn
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

    if request.user not in room.players.all():
        return redirect('start_game')
    
    card = get_object_or_404(Card, id=card_id)
    player_card = get_object_or_404(PlayerCard, player=request.user, card=card, room=room)

    last_played_card = room.last_played_card

    if room.turn == request.user:
        if last_played_card:
            if card.suit == last_played_card.suit or card.type == last_played_card.type or card.suit == 'S':
                room.last_played_card = card
                for player in room.players.all():
                    if player != request.user:
                        room.turn = player
                room.save()

                player_card.delete()

                handle_special_card(request, room)

                return redirect('game_room', room_name=room_name)
            else:
                messages.error(request, "You can't play this card.")
                return redirect('game_room', room_name=room_name)
        else:
            room.last_played_card = card
            room.save()
            player_card.delete()
            handle_special_card(room, card)
            return redirect('game_room', room_name=room_name)
    return redirect('game_room', room_name=room_name)


def handle_special_card(request, room):
    if room.last_played_card.type == 'wild':
        pass
    elif room.last_played_card.type == 'wild_draw_4':
        pass
    elif room.last_played_card.type == 'S':
        room.turn = request.user
        room.save()
        messages.success(request, f"Skip card, {request.user}")
        pass
    elif room.last_played_card.type == 'R':
        room.turn = request.user
        room.save()
        messages.success(request, f"Reverse card, {request.user}")
        pass
    elif room.last_played_card.type == 'draw_2':
        pass


