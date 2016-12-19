from django.db import models


# Create your models here.

class Users(models.Model):
    twitch_username = models.CharField(max_length=36, primary_key=True, unique=True)


class Stats(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    viewers = models.IntegerField()
    followers = models.IntegerField()
    views = models.IntegerField()
    game = models.CharField(max_length=200)