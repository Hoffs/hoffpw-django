"""
    Settings for Twitch Stats app.
"""

# Twitch App settings
import os

TWITCH_CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID', '')
TWITCH_CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET', '')
TWITCH_REDIRECT_URI = "https://hoff.pw/twitch/callback"
TWITCH_VERSION_HEADERS = "application/vnd.twitchtv.v5+json"

try:
    from .local_settings import *
except ImportError:
    pass
