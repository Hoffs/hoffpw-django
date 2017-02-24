import uuid

import django_celery_beat
from django.db import models
import requests
import dateutil.parser
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from .settings import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_REDIRECT_URI, TWITCH_VERSION_HEADERS


class TwitchProfileManager(models.Manager):
    def get_from_id_or_username_or_uuid(self, identifier):
        response = self.get_from_uuid(identifier)
        if response:
            return response

        response = self.get_from_username(identifier)
        if response:
            return response

        response = self.get_from_id(identifier)
        if response:
            return response
        else:
            return None

    def get_from_uuid(self, identifier):
        try:
            from uuid import UUID
            user_id = UUID(identifier, version=4)
            try:
                obj = self.model.objects.get(user=user_id)
                return obj
            except self.model.DoesNotExist:
                return None
        except ValueError:
            return None

    def get_from_username(self, identifier):
        try:
            obj = self.model.objects.get(twitch_name=identifier.lower())
            return obj
        except self.model.DoesNotExist:
            return None

    def get_from_id(self, identifier):
        try:
            obj = self.model.objects.get(twitch_id=identifier)
            return obj
        except self.model.DoesNotExist:
            return None

    def create_from_code(self, code=None, **kwargs):
        user = kwargs.pop('user')
        if self.filter(user=user).count() > 0:
            return "Account already linked.", False
        token, refresh_token, scope = self._get_oauth(code=code)
        if token is None:
            return "Unauthorized token.", False
        response = self._get_user_info(token=token)
        twitch_id = response['_id']
        if self.filter(twitch_id=twitch_id).count() > 0:
            return "Twitch account already linked.", False
        twitch_email = response['email']
        twitch_display = response['display_name']
        twitch_name = response['name']
        twitch_partnered = response['partnered']
        twitch_type = response['type']
        twitch_created = dateutil.parser.parse(response['created_at'])
        self.create(twitch_id=twitch_id, twitch_name=twitch_name, twitch_display=twitch_display,
                    twitch_email=twitch_email, twitch_is_partnered=twitch_partnered,
                    twitch_user_type=twitch_type,
                    twitch_created=twitch_created, authorization_code=code, access_token=token, scopes=scope,
                    user=user)
        return "Successfully linked profile.", True

    def _get_oauth(self, code=None):
        state = uuid.uuid4()
        url = "https://api.twitch.tv/kraken/oauth2/token?client_id={0}&client_secret={1}&" \
              "grant_type=authorization_code&redirect_uri={2}&code={3}&state={4}".format(TWITCH_CLIENT_ID,
                                                                                         TWITCH_CLIENT_SECRET,
                                                                                         TWITCH_REDIRECT_URI,
                                                                                         code,
                                                                                         state)
        r = requests.post(url=url)
        if 'error' in r.json():
            return None, None, None
        token = r.json()['access_token']
        refresh_token = r.json()['refresh_token']
        scopes = r.json()['scope']
        return token, refresh_token, scopes

    def _get_user_info(self, token=None):
        url = "https://api.twitch.tv/kraken/user"
        headers = {'Accept': TWITCH_VERSION_HEADERS, 'Client-ID': TWITCH_CLIENT_ID,
                   'Authorization': 'OAuth {}'.format(token)}
        r = requests.get(url=url, headers=headers)
        return r.json()


class TwitchTrackingProfileManager(models.Manager):
    def get_or_create(self, t_id=None):
        if not t_id:
            return None
        try:
            profile = self.get(twitch_id=t_id)
            return profile
        except self.model.DoesNotExist:
            is_true, t_name = self._verify_id(t_id=t_id)
            if is_true:
                return self.create(twitch_id=t_id, twitch_name=t_name)
        return None

    def can_delete(self, obj=None):
        if obj.tracking_profile.count() > 0:
            return False
        else:
            return True

    @staticmethod
    def _verify_id(t_id=None):
        if t_id:
            url = "https://api.twitch.tv/kraken/users/{}".format(t_id)
            headers = {'Accept': TWITCH_VERSION_HEADERS, 'Client-ID': TWITCH_CLIENT_ID}
            r = requests.get(url=url, headers=headers)
            r_id = r.json().get('_id')
            r_name = r.json().get('name')
            if r_id and r_name and t_id == r_id:
                return True, r_name
            else:
                return False, None
        else:
            return False, None

    def get_from_id_or_name_with_user(self, identifier=None, user=None):
        response = self.get_from_username(identifier=identifier, user=user)
        if response:
            return response

        response = self.get_from_id(identifier=identifier, user=user)
        if response:
            return response
        else:
            return None

    def get_from_username(self, identifier=None, user=None):
        try:
            obj = self.model.objects.get(twitch_name=identifier.lower(), tracking_profile=user)
            return obj
        except self.model.DoesNotExist:
            return None

    def get_from_id(self, identifier, user=None):
        try:
            obj = self.model.objects.get(twitch_id=identifier, tracking_profile=user)
            return obj
        except self.model.DoesNotExist:
            return None


class TwitchStatsManager(models.Manager):
    def get_stats(self, twitch_id=None):
        if not twitch_id:
            return
        url = "https://api.twitch.tv/kraken/streams/{}".format(twitch_id)
        headers = {'Accept': TWITCH_VERSION_HEADERS, 'Client-ID': TWITCH_CLIENT_ID}
        r = requests.get(url=url, headers=headers)
        stream = r.json()['stream']
        if stream:
            stats = self.create(
                stream_id=stream['_id'],
                game=stream['game'],
                delay=stream['delay'],
                went_live=stream['created_at'],
                average_fps=stream['average_fps'],
                current_viewers=stream['viewers'],
                channel_id=stream['channel']['_id'],
                channel_status=stream['channel']['status'],
                channel_mature=stream['channel']['mature'],
                channel_language=stream['channel']['broadcaster_language'],
                is_playlist=stream['is_playlist'],
                is_partner=stream['channel']['partner'],
                total_views=stream['channel']['views'],
                total_followers=stream['channel']['followers']
            )
            return True
        return False

    def start_collecting(self, interval=1):
        if PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').count() == 0:
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=interval,
                period=IntervalSchedule.MINUTES,
            )

            task = PeriodicTask.objects.create(
                interval=schedule,
                name='Collecting statistics',
                task='twitch_stats.tasks.get_all_stats',
            )
            return True
        elif PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').count() > 0:
            task = PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').first()
            if not task.enabled:
                task.enabled = True
                task.save()
                return True
            else:
                return False

    def stop_collecting(self):
        if PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').count() == 1:
            task = PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').first()
            if task.enabled:
                task.enabled = False
                task.save()
                return True
            else:
                return False
        elif PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').count() > 1:
            PeriodicTask.objects.all().delete()
            return True
        else:
            return False

    def update_collecting(self, interval=5):
        if PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').count() == 1:
            schedule, created = IntervalSchedule.objects.get_or_create(
                every=interval,
                period=IntervalSchedule.MINUTES,
            )
            task = PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').first()
            task.interval = schedule
            task.save()
            return True
        else:
            return False

    def info_collecting(self):
        print(django_celery_beat.__version__)
        if PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').count() == 1:
            task = PeriodicTask.objects.filter(task='twitch_stats.tasks.get_all_stats').first()
            return task
        else:
            return None