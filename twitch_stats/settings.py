"""
    Settings for Twitch Stats app.
"""

# Twitch App settings
import os

TWITCH_CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID', '')
TWITCH_CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET', '')
TWITCH_REDIRECT_URI = "https://hoff.pw/twitch/callback"
TWITCH_VERSION_HEADERS = "application/vnd.twitchtv.v5+json"


"""
    God token used for testing is a random token that allows to do
    certain tasks without diving into admin/group/permission work yet.
    It should be later removed for an appropriate (is_admin() or something) solution.
"""
GOD_TOKEN = os.environ.get('GOD_TOKEN', '')

try:
    from .local_settings import *
except ImportError:
    pass