from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'order',
            'amount',
            'status',
            'razorpay_order_id',
            'razorpay_payment_id',
            'razorpay_signature',
            'created_at',
        ]
        read_only_fields = ['user', 'status', 'created_at']
