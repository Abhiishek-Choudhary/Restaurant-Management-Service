from django.urls import path
from .views import CartView, AddToCartView, UpdateCartItemView, RemoveCartItemView, ClearCartView

urlpatterns = [
    path('', CartView.as_view(), name='view-cart'),
    path('add/', AddToCartView.as_view(), name='add-to-cart'),
    path('update/<int:item_id>/', UpdateCartItemView.as_view(), name='update-cart'),
    path('remove/<int:item_id>/', RemoveCartItemView.as_view(), name='remove-cart-item'),
    path('clear/', ClearCartView.as_view(), name='clear-cart'),
]
