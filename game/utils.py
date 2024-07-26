import random
from .models import Card, GameRoom

import random
from .models import Card, GameRoom

def deal_cards(room):
    players = list(room.players.all())
    
    all_cards = list(Card.objects.all())
    random.shuffle(all_cards)
    
    player_hands = {player.id: [] for player in players}  # Используйте ID пользователя в качестве ключа
    
    for player in players:
        player_hands[player.id] = all_cards[:7]
        all_cards = all_cards[7:]
    
    initial_card_found = False
    for player_id in player_hands:
        non_special_cards = [card for card in player_hands[player_id] if card.suit in ['R', 'G', 'B', 'Y']]
        if non_special_cards:
            initial_card = random.choice(non_special_cards)
            room.last_played_card = initial_card
            room.save()
            player_hands[player_id].remove(initial_card)
            initial_card_found = True
            break

    if not initial_card_found:
        raise Exception("Не удалось найти подходящую начальную карту")

    return player_hands

