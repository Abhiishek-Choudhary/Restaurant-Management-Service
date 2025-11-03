# users/middleware.py
import jwt
from django.conf import settings
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import UntypedToken
from jwt import InvalidTokenError

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None

class JwtAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that takes ?token=<access_token> on websocket URL and populates scope['user'].
    """

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token = None
        if query_string:
            # parse query params simply
            for part in query_string.split("&"):
                if part.startswith("token="):
                    token = part.split("=", 1)[1]
                    break

        if token:
            try:
                # Validate token (raises if invalid)
                UntypedToken(token)
                # Decode to get payload (user id)
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded.get("user_id") or decoded.get("user_id") or decoded.get("user_id")
                user = await get_user(user_id)
                scope['user'] = user if user is not None else AnonymousUser()
            except Exception as e:
                # invalid token
                from django.contrib.auth.models import AnonymousUser
                scope['user'] = AnonymousUser()
        else:
            from django.contrib.auth.models import AnonymousUser
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
