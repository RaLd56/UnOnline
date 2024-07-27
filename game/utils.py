import random
from .models import Card, PlayerCard
from django.db import transaction

def deal_cards(room):
    players = room.players.all()
    all_cards = list(Card.objects.all())
    
    with transaction.atomic():
        room.player_cards.all().delete()
    
        random.shuffle(all_cards)

        for player in players:
            hand_cards = all_cards[:7]
            all_cards = all_cards[7:]
            for card in hand_cards:
                PlayerCard.objects.create(player=player, card=card, room=room)

        non_special_cards = [card for card in all_cards if card.suit in ['R', 'G', 'B', 'Y']]

        initial_card = random.choice(non_special_cards)
        room.last_played_card = initial_card
        room.save()

        room.turn = random.choice(players)
        room.save()
            
        

