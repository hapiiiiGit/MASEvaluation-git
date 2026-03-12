from rest_framework import viewsets, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    """

    def has_permission(self, request, view):
        # Allow read-only for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow write for admin users
        return request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role.name == 'Admin'

class AuditLogViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on AuditLog.
    """
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        # Only admins can create audit logs manually; usually logs are created automatically
        serializer.save(user=self.request.user)