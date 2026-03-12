from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Supplier, PurchaseOrder, PurchaseOrderLine
from .serializers import SupplierSerializer, PurchaseOrderSerializer, PurchaseOrderLineSerializer

class IsProcurementOrAccountantOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow procurement officers, accountants, or admins to edit objects.
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
        return role.name in ['Procurement Officer', 'Accountant', 'Admin']

class SupplierViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on Supplier.
    """
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsProcurementOrAccountantOrAdmin]

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on PurchaseOrder.
    """
    queryset = PurchaseOrder.objects.all().order_by('-date', '-id')
    serializer_class = PurchaseOrderSerializer
    permission_classes = [IsProcurementOrAccountantOrAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def lines(self, request, pk=None):
        """
        Get all lines for a specific purchase order.
        """
        purchase_order = self.get_object()
        lines = purchase_order.lines.all()
        serializer = PurchaseOrderLineSerializer(lines, many=True)
        return Response(serializer.data)

class PurchaseOrderLineViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on PurchaseOrderLine.
    """
    queryset = PurchaseOrderLine.objects.all()
    serializer_class = PurchaseOrderLineSerializer
    permission_classes = [IsProcurementOrAccountantOrAdmin]