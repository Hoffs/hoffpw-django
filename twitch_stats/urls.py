from django.conf.urls import include
from django.conf.urls import url
from rest_framework_nested import routers

from twitch_stats.views import TwitchProfileViewSet, TwitchTrackingProfileViewSet, TrackingView, TwitchStatsViewSet

router = routers.DefaultRouter()
router.register(r'profiles', TwitchProfileViewSet)

profile_router = routers.NestedSimpleRouter(router, r'profiles', lookup='profiles')
profile_router.register(r'tracking', TwitchTrackingProfileViewSet, base_name='twitch-tracking')

twitch_patterns = [
    url(r'', include(router.urls)),
    url(r'', include(profile_router.urls)),
    url(r'stats/(?P<pk>[^/.]+)/$', TwitchStatsViewSet.as_view({'get': 'list'})),
    url(r'settings/tracking/$', TrackingView.as_view()),
]