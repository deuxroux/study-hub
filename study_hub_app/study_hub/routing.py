from django.urls import re_path
from . import consumers

# USE OF ws/ as websocket url
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<pk>\d+)/$', consumers.ChatConsumer.as_asgi()),
]
