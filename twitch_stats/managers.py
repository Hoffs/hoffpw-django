import uuid

from django.db import models
import requests
import dateutil.parser

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
