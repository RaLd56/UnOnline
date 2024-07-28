from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GameRoom, Card, PlayerCard
from .forms import GameRoomForm, JoinRoomForm, ChooseColorForm
from .utils import deal_cards
from django.http import HttpResponseForbidden
from django.contrib import messages
import random


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
                    if request.user in room.players.all():
                        return redirect('game_room', room_name=room.name)
                    else:
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
    player_card = PlayerCard.objects.filter(player=request.user, card=card, room=room).first()

    last_played_card = room.last_played_card

    

    if room.turn == request.user:
        if last_played_card:
            if card.suit == room.chosen_suit or card.suit == room.last_played_card.suit or card.type == last_played_card.type or card.suit == 'S':
                room.last_played_card = card
                PlayerCard.objects.filter(player=request.user, card=card, room=room).first().delete()
                room.save()

                if room.chosen_suit:
                    room.chosen_suit = last_played_card.suit
                
                if card.type == 'W' or card.type == 'WD':
                    return redirect('choose_color', room_name=room_name)
                
                next_turn = room.players.exclude(id=request.user.id).first()
                room.turn = next_turn
                room.save()
                    
                handle_special_card(request, room, card)
                


                remaining_cards = room.player_cards.filter(player=request.user).count()
                if remaining_cards == 0:
                    if room.uno_declared:
                        messages.success(request, "Congratulations, you won the game!")
                        room.uno_declared = False
                        room.save()
                    else:
                        messages.error(request, "You didn't call Uno! You get 2 extra cards.")
                        for i in range(2):
                            get_extra_card(request, room.name)
                        room.uno_declared = False
                        room.save()
                else:
                    room.uno_declared = False
                    room.save()

                return redirect('game_room', room_name=room_name)
                
            else:
                messages.error(request, "You can't play this card.")
                return redirect('game_room', room_name=room_name)
        else:
            
            return redirect('game_room', room_name=room_name)
    else:
        messages.error(request, "It's not your turn")
        return redirect('game_room', room_name=room_name)
    


@login_required
def choose_color(request, room_name):
    room = get_object_or_404(GameRoom, name=room_name)
    if room.last_played_card.type == 'WD':
        give_extra_cards(request, room, 2)
        messages.success(request, f"Plus 4 cards for your opponent, {request.user}")
        


    if request.method == 'POST':
        form = ChooseColorForm(request.POST)
        if form.is_valid():
            chosen_color = form.cleaned_data['color']
            is_wild_draw = form.cleaned_data.get('wd', False)
            room.chosen_suit = chosen_color
            room.save()

            next_turn = room.players.exclude(id=request.user.id).first()
            room.turn = next_turn
            room.save()

            return redirect('game_room', room_name=room_name)
    else:
        form = ChooseColorForm()

    return render(request, 'game/choose_color.html', {'form': form, 'room': room})


def give_extra_cards(request, room, num):
    all_cards = list(Card.objects.all())
    random.shuffle(all_cards)
    extra_cards = all_cards[:num]
    for player in room.players.all():
            if player != request.user:
                next_player = player

    for card in extra_cards:
        PlayerCard.objects.create(player=next_player, card=card, room=room)

@login_required
def uno(request, room_name):
    room = get_object_or_404(GameRoom, name=room_name)
    player = request.user

    if player not in room.players.all():
        return redirect('start_game')

    
    if room.turn != player:
        return redirect('game_room', room_name=room_name)

    
    player_hand = room.player_cards.filter(player=player)
    card_count = player_hand.count()

    if card_count > 1:
        messages.error(request, "You need to have only one card to call Uno.")
        return redirect('game_room', room_name=room_name)

    # Устанавливаем состояние "Uno" для текущего игрока
    room.uno_declared = True
    room.save()

    # Проверка, если у игрока только одна карта
    if card_count == 1:
        messages.success(request, "You have declared Uno! Play your last card to win.")
        return redirect('game_room', room_name=room_name)

    return redirect('game_room', room_name=room_name)


def handle_special_card(request, room, card=None):
    if card is None:
        card = room.last_played_card

    if card.type == 'W':  # Wild Card
        return render(request, 'game/choose_color.html', {'form': ChooseColorForm(), 'room': room})

    elif card.type == 'WD':  # Wild Draw Four
        return render(request, 'game/choose_color.html', {'form': ChooseColorForm(), 'room': room, 'wd': True})

    elif card.type == 'S':
        room.turn = request.user
        room.save()
        messages.success(request, f"One more turn for you, {request.user}")
        return redirect('game_room', room_name=room.name)

    elif card.type == 'R':
        room.turn = request.user
        room.save()
        messages.success(request, f"One more turn for you, {request.user}")
        return redirect('game_room', room_name=room.name)

    elif card.type == 'D':
        give_extra_cards(request, room, 2)
        messages.success(request, f"Plus 2 cards for your opponent, {request.user}")



@login_required
def get_extra_card(request, room_name):
    room = get_object_or_404(GameRoom, name=room_name)
    player = request.user

    if player not in room.players.all():
        return redirect('start_game')
    
    all_cards = list(Card.objects.all())
    extra_card = random.choice(all_cards)

    PlayerCard.objects.create(player=player, card=extra_card, room=room)
    
    return redirect('game_room', room_name=room_name)