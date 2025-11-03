from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import Order
from .serializers import OrderSerializer
from users.models import User

# Custom permission
class IsAdminRole(BasePermission):
    """
    Allows access only to users with role 'Admin'.
    """
    message = "You must be an admin to access this resource."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'role', None) == 'ADMIN'


# Admin views
class AdminOrderListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, order_id):
        status = request.data.get("status")
        valid_status = [
            "PENDING", "ACCEPTED", "PREPARING",
            "OUT_FOR_DELIVERY", "DELIVERED", "REJECTED"
        ]

        if status not in valid_status:
            return Response({"error": "Invalid status"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
            order.status = status
            order.save()
            return Response({"message": "Order status updated"})
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)


class AssignDeliveryBoyView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, order_id):
        delivery_boy_id = request.data.get("delivery_boy_id")

        try:
            order = Order.objects.get(id=order_id)
            delivery_boy = User.objects.get(id=delivery_boy_id, role="DELIVERY")

            order.delivery_boy = delivery_boy
            order.status = "OUT_FOR_DELIVERY"
            order.save()

            return Response({"message": "Delivery boy assigned"})
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)
        except User.DoesNotExist:
            return Response({"error": "Invalid delivery boy"}, status=404)
