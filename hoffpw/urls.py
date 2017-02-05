"""hoffpw URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers

from twitch_stats.views import TwitchProfileViewSet, TwitchProfileConnect
from webauth.views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'twitch', TwitchProfileViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/login/', ObtainAuthToken.as_view()),
    url(r'^auth/logout/', InvalidateToken.as_view()),
    url(r'^admin/', admin.site.urls),
    url(r'^api/twitch/callback/', TwitchProfileConnect.as_view()),
    url(r'^password/reset/$', PasswordReset.as_view()),
    url(r'^password/reset/confirm/$', PasswordResetConfirm.as_view()),
    url(r'^email/confirm/$', UserEmailConfirm.as_view()),
    url(r'^email/request/$', UserEmailConfirmRequest.as_view()),
]
