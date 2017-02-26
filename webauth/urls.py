from django.conf.urls import url, include
from rest_framework import routers

from webauth.views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

auth_patterns = [
    url(r'', include(router.urls)),
    url(r'auth/login/', ObtainToken.as_view()),
    url(r'auth/logout/', InvalidateToken.as_view()),
    url(r'auth/email/confirm/$', UserEmailConfirm.as_view()),
    url(r'auth/email/request/$', UserEmailConfirmRequest.as_view()),
    url(r'auth/password/reset/$', PasswordReset.as_view()),
    url(r'auth/password/reset/confirm/$', PasswordResetConfirm.as_view()),
]