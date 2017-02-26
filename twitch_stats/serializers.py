from rest_framework import serializers

from twitch_stats.models import TwitchProfile, TwitchTrackingProfile, TwitchStats


class TwitchProfileSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for getting information about twitch user profile.
    """

    class Meta:
        model = TwitchProfile
        fields = ('user', 'twitch_id', 'twitch_display', 'twitch_name', 'twitch_is_partnered', 'twitch_created',)


class TwitchProfileRegisterSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for registering new users.
    """
    code = serializers.CharField(max_length=254)

    class Meta:
        model = TwitchProfile
        fields = ('code',)


class TwitchAddTrackingSerializer(serializers.Serializer):
    """
    Serializer for adding user to track.
    """
    twitch_id = serializers.CharField(max_length=254)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class TwitchTrackingSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for displaying tracked users by a profile.
    """

    class Meta:
        model = TwitchTrackingProfile
        fields = ('twitch_id',)

class TwitchStatsSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for retrieving Twitch Stats.
    """

    class Meta:
        model = TwitchStats
        fields = ('channel_id', 'stream_id', 'channel_status', 'current_viewers', 'total_views', 'total_followers')


class TrackingSchedulerSerializer(serializers.Serializer):
    """
    Serializer for starting and stopping stats collection scheduled task.
    """

    command = serializers.CharField()
    interval = serializers.CharField(default=5)
    token = serializers.CharField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
