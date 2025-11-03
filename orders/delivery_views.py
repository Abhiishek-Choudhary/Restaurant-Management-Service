from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer

class DeliveryOrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != "DELIVERY":
            return Response({"error": "Not authorized"}, status=403)

        orders = Order.objects.filter(delivery_boy=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class UpdateDeliveryStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        if request.user.role != "DELIVERY":
            return Response({"error": "Not authorized"}, status=403)

        status = request.data.get("status")

        if status not in ["OUT_FOR_DELIVERY", "DELIVERED"]:
            return Response({"error": "Invalid status"}, status=400)

        try:
            order = Order.objects.get(id=order_id, delivery_boy=request.user)
            order.status = status
            order.save()
            return Response({"message": "Status updated"})
        except Order.DoesNotExist:
            return Response({"error": "Order not found or not assigned to you"}, status=404)
