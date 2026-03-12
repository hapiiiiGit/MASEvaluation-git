from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Invoice, InvoiceLine
from .serializers import InvoiceSerializer, InvoiceLineSerializer

class IsSalesManagerOrAccountantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow sales managers, accountants, or admins to edit objects.
    """

    def has_permission(self, request, view):
        # Allow read-only for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        role = getattr(user, 'role', None)
        if not role:
            return False
        return role.name in ['Sales Manager', 'Accountant', 'Admin']

class InvoiceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on Invoice.
    """
    queryset = Invoice.objects.all().order_by('-date', '-id')
    serializer_class = InvoiceSerializer
    permission_classes = [IsSalesManagerOrAccountantOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def lines(self, request, pk=None):
        """
        Get all lines for a specific invoice.
        """
        invoice = self.get_object()
        lines = invoice.lines.all()
        serializer = InvoiceLineSerializer(lines, many=True)
        return Response(serializer.data)

class InvoiceLineViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on InvoiceLine.
    """
    queryset = InvoiceLine.objects.all()
    serializer_class = InvoiceLineSerializer
    permission_classes = [IsSalesManagerOrAccountantOrReadOnly]