from django.utils.translation import ugettext_lazy as _
from django.db import models

from hoffpw import settings


class TwitchProfile(models.Model):
    twitch_id = models.CharField(max_length=254, primary_key=True)
    twitch_user = models.CharField(max_length=254)
    should_track = models.BooleanField(default=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='twitch_profile',
        on_delete=models.CASCADE, verbose_name=_("User"),
        primary_key=True
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    updated = models.DateTimeField(_("Updated"), auto_now=True)

    class Meta:
        verbose_name = _("Twitch profile")
        verbose_name_plural = _("Twitch profiles")


class TwitchStats(models.Model):
    """
    Todo
    """
    pass
