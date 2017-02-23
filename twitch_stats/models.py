from django.utils.translation import ugettext_lazy as _
from django.db import models

from hoffpw import settings
from twitch_stats.managers import TwitchProfileManager, TwitchTrackingProfileManager, TwitchStatsManager


class TwitchProfile(models.Model):
    twitch_id = models.TextField()
    twitch_name = models.TextField()
    twitch_display = models.TextField()
    twitch_email = models.EmailField()
    twitch_is_partnered = models.BooleanField(default=False)
    twitch_user_type = models.TextField()
    twitch_created = models.DateTimeField()
    authorization_code = models.TextField()
    access_token = models.TextField()
    scopes = models.TextField()
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='user',
        verbose_name=_("User"), primary_key=True
    )
    tracking_users = models.ManyToManyField(
        'TwitchTrackingProfile', related_name='tracking_profile',
        verbose_name=_("Tracking")
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)

    REQUIRED_FIELDS = ['twitch_id', 'twitch_name', 'user', 'authorization_code', 'access_token']

    objects = TwitchProfileManager()

    class Meta:
        verbose_name = _("Twitch profile")
        verbose_name_plural = _("Twitch profiles")


class TwitchTrackingProfile(models.Model):
    twitch_id = models.TextField(max_length=254)
    twitch_name = models.TextField(max_length=254)

    objects = TwitchTrackingProfileManager()


class TwitchStats(models.Model):
    stream_id = models.TextField()
    game = models.TextField()
    delay = models.FloatField()
    average_fps = models.FloatField()
    current_viewers = models.IntegerField()
    channel_id = models.TextField()
    channel_status = models.TextField()
    channel_mature = models.BooleanField(default=False)
    channel_language = models.TextField()
    went_live = models.DateTimeField()
    is_playlist = models.BooleanField(default=False)
    is_partner = models.BooleanField(default=False)
    total_views = models.BigIntegerField()
    total_followers = models.BigIntegerField()

    objects = TwitchStatsManager()