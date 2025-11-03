from rest_framework import serializers
from .models import Cart, CartItem
from restaurant.models import MenuItem

class CartItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.ReadOnlyField(source='menu_item.name')
    price = serializers.ReadOnlyField(source='menu_item.price')

    class Meta:
        model = CartItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'notes', 'price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        return sum(item.menu_item.price * item.quantity for item in obj.items.all())


class AddToCartSerializer(serializers.Serializer):
    menu_item = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        try:
            MenuItem.objects.get(id=data['menu_item'])
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError("Menu item does not exist")
        return data
