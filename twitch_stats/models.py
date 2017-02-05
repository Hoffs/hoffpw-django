from django.utils.translation import ugettext_lazy as _
from django.db import models

from hoffpw import settings
from twitch_stats.managers import TwitchProfileManager


class TwitchProfile(models.Model):
    twitch_id = models.CharField(max_length=254)
    twitch_name = models.CharField(max_length=254)
    twitch_display = models.CharField(max_length=254)
    twitch_email = models.EmailField()
    twitch_is_partnered = models.BooleanField(default=False)
    twitch_user_type = models.CharField(max_length=254)
    twitch_created = models.DateTimeField()
    authorization_code = models.CharField(max_length=254)
    access_token = models.CharField(max_length=254)
    scopes = models.CharField(max_length=254)
    should_track = models.BooleanField(default=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='twitch_profile',
        on_delete=models.CASCADE, verbose_name=_("User"),
        primary_key=True
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)

    REQUIRED_FIELDS = ['twitch_id', 'twitch_name', 'authorization_code', 'access_token']

    objects = TwitchProfileManager()

    class Meta:
        verbose_name = _("Twitch profile")
        verbose_name_plural = _("Twitch profiles")


class TwitchStats(models.Model):
    game = models.CharField(max_length=254)
    delay = models.FloatField()
    average_fps = models.FloatField()
    current_viewers = models.IntegerField()
    channel_id = models.CharField(max_length=254)
    channel_status = models.CharField(max_length=254)
    channel_mature = models.BooleanField(default=False)
    channel_language = models.CharField(max_length=64)
    channel_went_live = models.DateTimeField()
    is_playlist = models.BooleanField(default=False)
    is_partner = models.BooleanField(default=False)
    total_views = models.BigIntegerField()
    total_followers = models.BigIntegerField()
