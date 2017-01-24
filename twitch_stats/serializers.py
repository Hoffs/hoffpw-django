from rest_framework import serializers

from twitch_stats.models import TwitchProfile


class TwitchProfileSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for getting information about twitch user profile.
    """

    class Meta:
        model = TwitchProfile
        fields = ('user', 'twitch_id', 'should_track',)


class TwitchProfileRegisterSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for registering new users.
    """

    class Meta:
        model = TwitchProfile
        fields = ('twitch_id', 'twitch_user',)
