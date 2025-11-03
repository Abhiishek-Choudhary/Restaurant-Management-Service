from django.urls import path
from .views import KitchenOrderListView, KitchenUpdateOrderStatusView

urlpatterns = [
    path('orders/', KitchenOrderListView.as_view(), name='kitchen-orders'),
    path('orders/<int:id>/update-status/', KitchenUpdateOrderStatusView.as_view(), name='kitchen-update-order'),
]
