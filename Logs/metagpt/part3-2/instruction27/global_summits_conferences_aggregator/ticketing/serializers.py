from rest_framework import serializers
from .models import Ticket, Order, Payment
from events.models import Event
from users.models import User

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'profile_picture']

class EventShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'event_type', 'start_date', 'end_date', 'location']

class TicketSerializer(serializers.ModelSerializer):
    event = EventShortSerializer(read_only=True)
    issued_to = UserShortSerializer(read_only=True)
    qr_code = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Ticket
        fields = [
            'id', 'event', 'ticket_type', 'price', 'status', 'issued_to',
            'qr_code', 'created_at', 'updated_at'
        ]

class TicketCreateSerializer(serializers.ModelSerializer):
    qr_code = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Ticket
        fields = [
            'event', 'ticket_type', 'price', 'status', 'issued_to', 'qr_code'
        ]

class OrderSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    event = EventShortSerializer(read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'event', 'tickets', 'total_amount', 'status',
            'created_at', 'updated_at'
        ]

class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = serializers.PrimaryKeyRelatedField(
        queryset=Ticket.objects.all(), many=True
    )

    class Meta:
        model = Order
        fields = [
            'user', 'event', 'tickets', 'total_amount', 'status'
        ]

class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'provider', 'transaction_id', 'amount', 'status',
            'payment_date', 'refund_date', 'raw_response'
        ]

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'order', 'provider', 'transaction_id', 'amount', 'status', 'raw_response'
        ]