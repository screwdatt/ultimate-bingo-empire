from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/(?P<room_name>\w+)/$', consumers.BingoConsumer.as_asgi()),
    re_path(r'ws/host/(?P<room_name>\w+)/$', consumers.BingoConsumer.as_asgi()),
]
