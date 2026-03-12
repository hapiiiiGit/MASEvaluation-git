from rest_framework import views, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from events.models import Event
from users.models import User
from ticketing.models import Order, Payment
from events.serializers import EventSerializer
from users.serializers import UserSerializer
from ticketing.serializers import OrderSerializer, PaymentSerializer
from django.db.models import Count, Sum, Q
from rest_framework.permissions import IsAdminUser

class AdminDashboardPermission(permissions.BasePermission):
    """
    Custom permission to only allow admin users (role='admin' or is_superuser).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or getattr(request.user, 'role', None) == 'admin')

class AdminDashboardView(views.APIView):
    """
    Provides analytics and summary data for the admin dashboard.
    """
    permission_classes = [AdminDashboardPermission]

    def get(self, request, format=None):
        # User stats
        total_users = User.objects.count()
        delegates = User.objects.filter(role='delegate').count()
        organizers = User.objects.filter(role='organizer').count()
        speakers = User.objects.filter(role='speaker').count()
        admins = User.objects.filter(role='admin').count()

        # Event stats
        total_events = Event.objects.count()
        featured_events = Event.objects.filter(is_featured=True).count()
        upcoming_events = Event.objects.filter(start_date__gte=request.now()).count()
        past_events = Event.objects.filter(end_date__lt=request.now()).count()

        # Ticketing/Order stats
        total_orders = Order.objects.count()
        total_payments = Payment.objects.filter(status='successful').aggregate(total=Sum('amount'))['total'] or 0

        # Monetization: commission/fees (example: 10% commission)
        commission_rate = 0.10
        commission_earned = total_payments * commission_rate if total_payments else 0

        data = {
            "users": {
                "total": total_users,
                "delegates": delegates,
                "organizers": organizers,
                "speakers": speakers,
                "admins": admins,
            },
            "events": {
                "total": total_events,
                "featured": featured_events,
                "upcoming": upcoming_events,
                "past": past_events,
            },
            "orders": {
                "total": total_orders,
            },
            "payments": {
                "total_amount": total_payments,
                "commission_earned": commission_earned,
                "commission_rate": commission_rate,
            }
        }
        return Response(data, status=status.HTTP_200_OK)

class AdminEventViewSet(viewsets.ModelViewSet):
    """
    Allows admin to manage all events.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AdminDashboardPermission]

    @action(detail=True, methods=['post'])
    def feature(self, request, pk=None):
        """
        Mark an event as featured.
        """
        event = self.get_object()
        event.is_featured = True
        event.save()
        return Response({"detail": "Event marked as featured."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unfeature(self, request, pk=None):
        """
        Unmark an event as featured.
        """
        event = self.get_object()
        event.is_featured = False
        event.save()
        return Response({"detail": "Event unmarked as featured."}, status=status.HTTP_200_OK)

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    Allows admin to manage all users.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminDashboardPermission]

    @action(detail=True, methods=['post'])
    def promote(self, request, pk=None):
        """
        Promote a user to admin.
        """
        user = self.get_object()
        user.role = 'admin'
        user.save()
        return Response({"detail": "User promoted to admin."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def demote(self, request, pk=None):
        """
        Demote a user from admin to delegate.
        """
        user = self.get_object()
        if user.is_superuser:
            return Response({"detail": "Cannot demote a superuser."}, status=status.HTTP_400_BAD_REQUEST)
        user.role = 'delegate'
        user.save()
        return Response({"detail": "User demoted to delegate."}, status=status.HTTP_200_OK)

class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allows admin to view all orders.
    """
    queryset = Order.objects.all().select_related('user', 'event')
    serializer_class = OrderSerializer
    permission_classes = [AdminDashboardPermission]

class AdminPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Allows admin to view all payments.
    """
    queryset = Payment.objects.all().select_related('order')
    serializer_class = PaymentSerializer
    permission_classes = [AdminDashboardPermission]