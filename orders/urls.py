from django.urls import path
from .views import CreateOrderView, UserOrdersView
from .admin_views import AdminOrderListView, UpdateOrderStatusView, AssignDeliveryBoyView
from .delivery_views import DeliveryOrderListView, UpdateDeliveryStatusView

urlpatterns = [
    path('create/', CreateOrderView.as_view()),
    path('', UserOrdersView.as_view()),
]

urlpatterns += [
    path('admin/all/', AdminOrderListView.as_view()),
    path('admin/update/<int:order_id>/', UpdateOrderStatusView.as_view()),
    path('admin/assign-delivery/<int:order_id>/', AssignDeliveryBoyView.as_view()),
]

urlpatterns += [
    path('delivery/orders/', DeliveryOrderListView.as_view()),
    path('delivery/update/<int:order_id>/', UpdateDeliveryStatusView.as_view()),
]
