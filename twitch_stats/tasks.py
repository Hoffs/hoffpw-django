# Create your tasks here
from __future__ import absolute_import, unicode_literals

from celery import group
from celery import shared_task

from twitch_stats.models import TwitchTrackingProfile, TwitchStats


@shared_task()
def get_stats():
    objects = TwitchTrackingProfile.objects.all()
    object_list = list(objects)
    job = group(get_stats_by_id.s(obj.twitch_id) for obj in object_list)
    job.apply_async()

@shared_task()
def get_stats_by_id(tid):
    TwitchStats.objects.get_stats(twitch_id=tid)

@shared_task()
def get_track():
    objects = TwitchStats.objects.all()
    object_list = list(objects)
    return object_list
