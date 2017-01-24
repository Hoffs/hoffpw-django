from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from twitch_stats.models import TwitchProfile
from twitch_stats.serializers import TwitchProfileSerializer, TwitchProfileRegisterSerializer


class TwitchProfileViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                           mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = TwitchProfile.objects.all()
    serializer_class = TwitchProfileSerializer
    permission_classes = [AllowAny, ]

    def create(self, request, **kwargs):
        serializer = TwitchProfileRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True) and self.request.user.is_authenticated:
            TwitchProfile.objects.create(twitch_id=self.request.data['twitch_id'], twitch_user=self.request.data['twitch_user'],
                                         user=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Not authorized."}, status=status.HTTP_401_UNAUTHORIZED)
