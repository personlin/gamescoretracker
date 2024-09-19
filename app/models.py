from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    name = models.CharField(max_length=100)
    starting_score = models.IntegerField(default=0)
    increment = models.IntegerField(default=1)
    color = models.CharField(max_length=7)  # 存储颜色的 HEX 值
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class Game(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)
    players = models.ManyToManyField(Player, through='GameScore')
    
    def __str__(self):
        return self.name

class GameScore(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.game.name} - {self.player.name}: {self.score}"
    
    class Meta:
        unique_together = ('game', 'player')


class History(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    data = models.TextField()  # 可以存储 JSON 格式的比赛数据
    timestamp = models.DateTimeField(auto_now_add=True)
