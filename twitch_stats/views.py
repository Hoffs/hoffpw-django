from django.core import serializers
from django.http import Http404
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from twitch_stats.models import TwitchProfile, TwitchTrackingProfile, TwitchStats
from twitch_stats.serializers import TwitchProfileSerializer, TwitchProfileRegisterSerializer, \
    TwitchAddTrackingSerializer, TwitchTrackingSerializer, TrackingSchedulerSerializer

from twitch_stats.permissions import IsOwnerOrReadOnly
from twitch_stats.settings import GOD_TOKEN


class TwitchProfileViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                           mixins.DestroyModelMixin, viewsets.GenericViewSet):
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
        try:
            identifier = self.kwargs['pk']
        except KeyError:
            raise Http404
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
            try:
                return TwitchProfile.objects.filter(user=self.request.user)
            except TwitchProfile.DoesNotExist:
                return TwitchProfile.objects.none()
        else:
            return TwitchProfile.objects.none()


class TwitchTrackingProfileViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.DestroyModelMixin,
                                   mixins.CreateModelMixin, mixins.RetrieveModelMixin):
    queryset = TwitchTrackingProfile.objects.all()
    serializer_class = TwitchTrackingSerializer
    permission_classes = [AllowAny, IsOwnerOrReadOnly]

    def create(self, request, profile_pk=None, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        parent = self.get_parent()
        self.check_object_permissions(request=request, obj=parent)
        if serializer.is_valid(raise_exception=True):
            obj = TwitchTrackingProfile.objects.get_or_create(t_id=serializer.validated_data['twitch_id'])
            parent.tracking_users.add(obj)
            parent.save()
            return Response({'detail': 'Successfully added user to tracking list.'})
        return Response({'detail': 'Something went wrong.'})

    def get_object(self):
        try:
            identifier = self.kwargs['pk']
        except KeyError:
            raise Http404
        obj = TwitchTrackingProfile.objects.get_from_id_or_name(identifier=identifier)
        if obj:
            parent = self.get_parent()
            self.check_object_permissions(request=self.request, obj=parent)
            return obj
        else:
            raise Http404

    def get_parent(self):
        try:
            identifier = self.kwargs['profiles_pk']
        except KeyError:
            raise Http404
        obj = TwitchProfile.objects.get_from_id_or_username_or_uuid(identifier=identifier)
        if obj:
            return obj
        else:
            raise Http404

    def get_queryset(self):
        obj = self.get_parent()
        if obj:
            return obj.tracking_users.all()
        else:
            return TwitchTrackingProfile.objects.none()


class TrackingView(APIView):
    """
    View for starting and stopping scheduled task.
    """
    throttle_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = TrackingSchedulerSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['token'] != GOD_TOKEN:
            return Response({'detail': 'Unauthorized.'}, status=status.HTTP_401_UNAUTHORIZED)

        if serializer.validated_data['command'] == 'start':
            code = TwitchStats.objects.start_collecting(interval=serializer.validated_data['interval'])
            if code:
                return Response({'detail': 'Started collecting.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Task already running'}, status=status.HTTP_400_BAD_REQUEST)
        elif serializer.validated_data['command'] == 'stop':
            code = TwitchStats.objects.stop_collecting()
            if code:
                return Response({'detail': 'Stopped collecting.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'No tasks are running.'}, status=status.HTTP_404_NOT_FOUND)
        elif serializer.validated_data['command'] == 'update':
            code = TwitchStats.objects.update_collecting(interval=serializer.validated_data['interval'])
            if code:
                return Response({'detail': 'Task updated.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Task not updated'}, status=status.HTTP_400_BAD_REQUEST)
        elif serializer.validated_data['command'] == 'info':
            result = TwitchStats.objects.info_collecting()
            if result:
                return Response(serializers.serialize('json', [result]), status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Task not running.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'Invalid command.'}, status=status.HTTP_400_BAD_REQUEST)