from django.urls import path
from .views import create_payment_order, verify_payment

from .views import razorpay_webhook

urlpatterns = [
    path('create/', create_payment_order),
    path('verify/', verify_payment),
]

urlpatterns += [
    path('webhook/', razorpay_webhook),
]
