from django.http import Http404
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from twitch_stats.models import TwitchProfile
from twitch_stats.serializers import TwitchProfileSerializer, TwitchProfileRegisterSerializer
from rest_framework.views import APIView

from webauth.permissions import IsOwnerOrReadOnly


class TwitchProfileViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    """
    A simple ViewSet for viewing and editing twitch profiles.
    """
    queryset = TwitchProfile.objects.all()
    serializer_class = TwitchProfileSerializer
    permission_classes = [AllowAny, IsOwnerOrReadOnly]

    def create(self, request, **kwargs):
        serializer = TwitchProfileRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True) and request.user.is_authenticated():
            detail, is_created = TwitchProfile.objects.create_from_code(code=serializer.data['code'],
                                                                        user=request.user)
            if is_created:
                return Response({"detail": detail}, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": detail}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "Not authorized."}, status=status.HTTP_401_UNAUTHORIZED)

    def get_object(self):
        identifier = self.kwargs['pk']
        obj = TwitchProfile.objects.get_from_id_or_username_or_uuid(identifier=identifier)
        if obj:
            self.check_object_permissions(request=self.request, obj=obj)
            return obj
        else:
            raise Http404

    def get_queryset(self):
        if not self.request.user.is_anonymous and self.request.user.is_admin():
            return TwitchProfile.objects.all()
        elif not self.request.user.is_anonymous:
            return TwitchProfile.objects.filter(uuid=self.request.user.uuid)
        else:
            return TwitchProfile.objects.none()
