"""
ASGI config for restaurant_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import kitchen.routing
from users.middleware import JwtAuthMiddleware  # we'll add this

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')

# application = get_asgi_application()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JwtAuthMiddleware(
        URLRouter(
            kitchen.routing.websocket_urlpatterns
        )
    ),
})
