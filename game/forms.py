from django import forms
from .models import GameRoom

class GameRoomForm(forms.ModelForm):
    class Meta:
        model = GameRoom
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'maxlength': '10'})
        }

class JoinRoomForm(forms.Form):
    room_name = forms.CharField(max_length=10, label="Enter room name", widget=forms.TextInput(attrs={'maxlength': '10'}))

class ChooseColorForm(forms.Form):
    COLOR_CHOICES = [
        ('R', 'Red'),
        ('G', 'Green'),
        ('B', 'Blue'),
        ('Y', 'Yellow'),
    ]
    color = forms.ChoiceField(choices=COLOR_CHOICES, widget=forms.RadioSelect)