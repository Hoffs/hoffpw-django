from rest_framework import serializers

from twitch_stats.models import TwitchProfile


class TwitchProfileSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for getting information about twitch user profile.
    """

    class Meta:
        model = TwitchProfile
        fields = ('user', 'twitch_id', 'twitch_display', 'twitch_name', 'twitch_created', 'tracking_users',)


class TwitchProfileRegisterSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for registering new users.
    """
    code = serializers.CharField(max_length=254)

    class Meta:
        model = TwitchProfile
        fields = ('code',)
