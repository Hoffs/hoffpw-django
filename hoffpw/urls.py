from django.conf.urls import url, include
from django.contrib import admin

from twitch_stats.urls import twitch_patterns
from webauth.urls import auth_patterns


urlpatterns = [
    url(r'^', include(auth_patterns)),
    url(r'^twitch/', include(twitch_patterns)),
    url(r'^admin/', admin.site.urls),
]