from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Kitchen dashboard subscribes to /ws/kitchen/
    re_path(r'ws/kitchen/$', consumers.KitchenConsumer.as_asgi()),

    # User-specific updates: connect to /ws/orders/?token=... and send user-specific events
    re_path(r'ws/orders/$', consumers.UserOrderConsumer.as_asgi()),
]
