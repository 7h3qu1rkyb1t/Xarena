from django.db import models
from django.contrib.auth.models import User
from accounts.models import Game, Membership
from django.utils import timezone


class Tournament(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    players = models.ManyToManyField(User, blank=True, through="Subscription")
    max_players = models.IntegerField(default=100)
    tourney_type = models.CharField(max_length=20)
    price = models.IntegerField()
    time = models.DateTimeField()
    tourney_id = models.CharField(max_length=50)
    tourney_pass = models.CharField(max_length=15)
    first_prize = models.IntegerField()
    second_prize = models.IntegerField()
    third_prize = models.IntegerField()
    prize_per_kill = models.IntegerField(null=True, blank=True)

    def is_live(self):
        return True if self.time <= timezone.now() else False

    def __str__(self):
        return self.game.name

    def players_joined(self):
        return len(self.players.all())


class Subscription(models.Model):
    tourney = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, on_delete=models.CASCADE, null=True)
    subscription_id = models.AutoField(primary_key=True,)
    player_joined = models.BooleanField(default=False)

    def __str__(self):
        return self.player.username + "_" + self.tourney.game.name


