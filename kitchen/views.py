from rest_framework import generics, permissions, status
from users.permissions import IsKitchenStaff
from orders.models import Order
from orders.serializers import OrderSerializer
from rest_framework.response import Response
from orders.models import Order
from users.permissions import IsKitchenStaff
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



class KitchenOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsKitchenStaff]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.exclude(status='completed').order_by('-created_at')




class KitchenUpdateOrderStatusView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsKitchenStaff]
    queryset = Order.objects.all()
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")

        allowed_statuses = ["accepted", "preparing", "ready", "completed"]

        if new_status not in allowed_statuses:
            return Response({"error": "Invalid status"}, status=400)

        order.status = new_status
        order.save()
        
        channel_layer = get_channel_layer()
        data = {
            "type": "order_notification",
            "data": {
                "event": "order_status_updated",
                "order_id": order.id,
                "status": order.status,
            } 
        }

        # notify kitchen (so all kitchen clients update)
        async_to_sync(channel_layer.group_send)("kitchen", data)

        # notify the customer who placed it
        async_to_sync(channel_layer.group_send)(f"user_{order.user.id}", data)

        return Response({"message": f"Order status updated to {new_status}"})
