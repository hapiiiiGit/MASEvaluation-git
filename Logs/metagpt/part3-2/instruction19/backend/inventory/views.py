from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import InventoryItem, InventoryAdjustment
from .serializers import InventoryItemSerializer, InventoryAdjustmentSerializer

class IsInventoryManagerOrAccountantOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow inventory managers, accountants, or admins to edit objects.
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

class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on InventoryItem.
    """
    queryset = InventoryItem.objects.all().order_by('sku')
    serializer_class = InventoryItemSerializer
    permission_classes = [IsInventoryManagerOrAccountantOrAdmin]

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def adjustments(self, request, pk=None):
        """
        Get all adjustments for a specific inventory item.
        """
        item = self.get_object()
        adjustments = item.adjustments.all()
        serializer = InventoryAdjustmentSerializer(adjustments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def low_stock(self, request):
        """
        Get all items below their reorder level.
        """
        low_stock_items = InventoryItem.objects.filter(quantity__lte=models.F('reorder_level'))
        serializer = self.get_serializer(low_stock_items, many=True)
        return Response(serializer.data)

class InventoryAdjustmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on InventoryAdjustment.
    """
    queryset = InventoryAdjustment.objects.all().order_by('-date', '-id')
    serializer_class = InventoryAdjustmentSerializer
    permission_classes = [IsInventoryManagerOrAccountantOrAdmin]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)