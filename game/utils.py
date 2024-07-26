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

        initial_card_found = False
        for player in players:
            non_special_cards = room.player_cards.filter(player=player, card__suit__in=['R', 'G', 'B', 'Y'])
            if non_special_cards.exists():
                initial_card = random.choice(non_special_cards).card
                room.last_played_card = initial_card
                room.save()
                room.player_cards.filter(player=player, card=initial_card).delete()
                initial_card_found = True
                break

        if initial_card_found:
            room.turn = random.choice(players)
            room.save()
