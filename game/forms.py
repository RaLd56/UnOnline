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
    room_name = forms.CharField(max_length=10, label="Введите имя комнаты", widget=forms.TextInput(attrs={'maxlength': '10'}))


'''class RoomCreationForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'room_password']

class JoinRoomForm(forms.Form):
    room_name = forms.CharField(max_length=100)
    room_password = forms.CharField(widget=forms.PasswordInput)'''
