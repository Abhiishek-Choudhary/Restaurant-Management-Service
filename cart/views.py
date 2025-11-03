from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import CartItem, Cart
from .serializers import CartSerializer, AddToCartSerializer, CartItemSerializer
from restaurant.models import MenuItem


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.cart


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = request.user.cart
        menu_item = MenuItem.objects.get(id=serializer.validated_data['menu_item'])
        quantity = serializer.validated_data['quantity']
        notes = serializer.validated_data.get('notes', '')

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            menu_item=menu_item,
            notes=notes
        )

        if not created:
            cart_item.quantity += quantity
        
        cart_item.save()

        return Response({"message": "Item added to cart"}, status=200)


class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart=request.user.cart)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        serializer = CartItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Cart updated"}, status=200)


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart=request.user.cart)
            item.delete()
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        return Response({"message": "Item removed"}, status=200)


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.cart.items.all().delete()
        return Response({"message": "Cart cleared"}, status=200)
