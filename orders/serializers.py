from rest_framework import serializers
from .models import Order, OrderItem
from cart.models import CartItem

class OrderItemSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='menu_item.name')
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'item_name', 'quantity', 'notes', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'payment_status', 'total', 'created_at', 'items']

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
