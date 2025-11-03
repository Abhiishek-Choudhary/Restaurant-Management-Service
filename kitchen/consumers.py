# kitchen/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class KitchenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        # allow only kitchen staff
        if not user or not getattr(user, "is_authenticated", False) or getattr(user, "role", None) != "kitchen":
            await self.close(code=4001)
            return

        self.group_name = "kitchen"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from channel layer
    async def order_notification(self, event):
        # event contains 'type' and 'data'
        await self.send(text_data=json.dumps(event['data']))


class UserOrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4003)
            return

        self.user_group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user_group_name, self.channel_name)

    async def order_notification(self, event):
        await self.send(text_data=json.dumps(event['data']))
