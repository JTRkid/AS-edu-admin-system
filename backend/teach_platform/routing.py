from django.urls import re_path
from apps.scores.consumers import ScoreConsumer

websocket_urlpatterns = [
    re_path(r'ws/scores/$', ScoreConsumer.as_asgi()),
]
