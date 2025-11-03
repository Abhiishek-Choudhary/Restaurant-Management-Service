from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = request.user.cart
        items = cart.items.all()

        if not items:
            return Response({"error": "Cart is empty"}, status=400)

        order = Order.objects.create(user=request.user)
        total = 0

        for item in items:
            OrderItem.objects.create(
                order=order,
                menu_item=item.menu_item,
                quantity=item.quantity,
                notes=item.notes,
                price=item.menu_item.price
            )
            total += item.menu_item.price * item.quantity

        order.total = total
        order.save()

        cart.items.all().delete()  # clear cart after order
        
        channel_layer = get_channel_layer()
        data = {
            "type": "order_notification",
            "data": {
                "event": "order_created",
                "order_id": order.id,
                "total": str(order.total),
                "status": order.status,
                "created_at": order.created_at.isoformat(),
                # include minimal items info if desired
            }
        }
        # notify kitchen group
        async_to_sync(channel_layer.group_send)("kitchen", data)

        # notify specific user group (optional)
        async_to_sync(channel_layer.group_send)(f"user_{request.user.id}", data)

        return Response({"message": "Order placed successfully!"}, status=200)


class UserOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)



