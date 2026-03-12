from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Ticket, Order, Payment
from .serializers import (
    TicketSerializer,
    TicketCreateSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer
)
from events.models import Event
from users.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction
from .payments import process_stripe_payment, process_paypal_payment

class TicketViewSet(viewsets.ModelViewSet):
    """
    API endpoint for ticket CRUD operations.
    """
    queryset = Ticket.objects.all().select_related('event', 'issued_to')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TicketCreateSerializer
        return TicketSerializer

    def perform_create(self, serializer):
        ticket = serializer.save()
        ticket.status = 'available'
        ticket.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reserve(self, request, pk=None):
        """
        Reserve a ticket for the current user.
        """
        ticket = self.get_object()
        user = request.user
        if ticket.status != 'available':
            return Response({"detail": "Ticket is not available."}, status=status.HTTP_400_BAD_REQUEST)
        ticket.status = 'reserved'
        ticket.issued_to = user
        ticket.save()
        return Response({"detail": "Ticket reserved successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        """
        Cancel a reserved ticket.
        """
        ticket = self.get_object()
        user = request.user
        if ticket.issued_to != user:
            return Response({"detail": "You do not own this ticket."}, status=status.HTTP_403_FORBIDDEN)
        ticket.status = 'available'
        ticket.issued_to = None
        ticket.save()
        return Response({"detail": "Ticket reservation cancelled."}, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for order management.
    """
    queryset = Order.objects.all().select_related('user', 'event').prefetch_related('tickets')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        order = serializer.save()
        # Mark tickets as sold and assign to user
        for ticket in order.tickets.all():
            if ticket.status not in ['available', 'reserved']:
                raise Exception("Ticket is not available for purchase.")
            ticket.status = 'sold'
            ticket.issued_to = order.user
            ticket.save()
        order.status = 'completed'
        order.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def refund(self, request, pk=None):
        """
        Request a refund for an order.
        """
        order = self.get_object()
        user = request.user
        if order.user != user and not user.is_superuser:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        if order.status != 'completed':
            return Response({"detail": "Order is not eligible for refund."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'refunded'
        order.save()
        for ticket in order.tickets.all():
            ticket.status = 'refunded'
            ticket.save()
        payment = getattr(order, 'payment', None)
        if payment:
            payment.status = 'refunded'
            payment.refund_date = payment.payment_date
            payment.save()
        return Response({"detail": "Order refunded successfully."}, status=status.HTTP_200_OK)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payment processing.
    """
    queryset = Payment.objects.all().select_related('order')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PaymentCreateSerializer
        return PaymentSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        payment = serializer.save()
        provider = payment.provider
        order = payment.order
        amount = payment.amount

        # Process payment via Stripe or PayPal
        if provider == 'stripe':
            result = process_stripe_payment(order, amount)
        elif provider == 'paypal':
            result = process_paypal_payment(order, amount)
        else:
            result = {'status': 'successful', 'transaction_id': 'manual-' + str(payment.id), 'raw_response': 'Manual payment processed.'}

        payment.status = result.get('status', 'failed')
        payment.transaction_id = result.get('transaction_id', '')
        payment.raw_response = result.get('raw_response', '')
        payment.save()

        if payment.status == 'successful':
            order.status = 'completed'
            order.save()
            for ticket in order.tickets.all():
                ticket.status = 'sold'
                ticket.issued_to = order.user
                ticket.save()
        else:
            order.status = 'pending'
            order.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def refund(self, request, pk=None):
        """
        Refund a payment.
        """
        payment = self.get_object()
        user = request.user
        if payment.order.user != user and not user.is_superuser:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        if payment.status != 'successful':
            return Response({"detail": "Payment is not eligible for refund."}, status=status.HTTP_400_BAD_REQUEST)
        payment.status = 'refunded'
        payment.refund_date = payment.payment_date
        payment.save()
        order = payment.order
        order.status = 'refunded'
        order.save()
        for ticket in order.tickets.all():
            ticket.status = 'refunded'
            ticket.save()
        return Response({"detail": "Payment refunded successfully."}, status=status.HTTP_200_OK)