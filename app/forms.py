from django import forms
from .models import Player, Game

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'starting_score', 'increment', 'color', 'profile_image']

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['name']  # 移除 'players' 字段
