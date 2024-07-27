from django.db import models
from django.contrib.auth.models import User

class Card(models.Model):
    SUIT_CHOICES = [
        ('R', 'Red'),
        ('G', 'Green'),
        ('B', 'Blue'),
        ('Y', 'Yellow'),
        ('S', 'Special'),
    ]

    TYPE_CHOICES = [
        ('0', 'Zero'),
        ('1', 'One'),
        ('2', 'Two'),
        ('3', 'Three'),
        ('4', 'Four'),
        ('5', 'Five'),
        ('6', 'Six'),
        ('7', 'Seven'),
        ('8', 'Eight'),
        ('9', 'Nine'),
        ('D', 'Draw Two'),
        ('S', 'Skip'),
        ('R', 'Reverse'),
        ('W', 'Wild'),
        ('WD', 'Wild Draw Four'),
    ]

    suit = models.CharField(max_length=1, choices=SUIT_CHOICES)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)

    def __str__(self):
        return f'{self.get_suit_display()} {self.get_type_display()}'

class GameRoom(models.Model):
    name = models.CharField(max_length=10, unique=True)
    players = models.ManyToManyField(User, related_name='game_rooms')
    is_full = models.BooleanField(default=False)
    last_played_card = models.ForeignKey(Card, null=True, blank=True, on_delete=models.SET_NULL)
    turn = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='current_turn')

    def __str__(self):
        return self.name

    def add_player(self, user):
        if not self.is_full and user not in self.players.all():
            self.players.add(user)
            if self.players.count() >= 2:
                self.is_full = True
                self.save()

    def remove_player(self, user):
        if user in self.players.all():
            self.players.remove(user)
            if self.is_full and self.players.count() < 2:
                self.is_full = False
                self.save()

class PlayerCard(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player_cards')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    room = models.ForeignKey(GameRoom, on_delete=models.CASCADE, related_name='player_cards')


