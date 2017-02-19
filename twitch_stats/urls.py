from django.conf.urls import include
from django.conf.urls import url
from rest_framework_nested import routers

from twitch_stats.views import TwitchProfileViewSet, TwitchTrackingProfileViewSet

router = routers.DefaultRouter()
router.register(r'twitch', TwitchProfileViewSet)

profile_router = routers.NestedSimpleRouter(router, r'twitch', lookup='profiles')
profile_router.register(r'tracking', TwitchTrackingProfileViewSet, base_name='twitch-tracking')

twitch_patterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(profile_router.urls))
]