from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Account, JournalEntry, JournalEntryLine
from .serializers import AccountSerializer, JournalEntrySerializer, JournalEntryLineSerializer

class IsAccountantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow accountants or admins to edit objects.
    """

    def has_permission(self, request, view):
        # Allow read-only for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow write for users with role 'Accountant' or 'Admin'
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        role = getattr(user, 'role', None)
        if not role:
            return False
        return role.name in ['Accountant', 'Admin']

class AccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on Account.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAccountantOrReadOnly]

class JournalEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on JournalEntry.
    """
    queryset = JournalEntry.objects.all().order_by('-date', '-id')
    serializer_class = JournalEntrySerializer
    permission_classes = [IsAccountantOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def lines(self, request, pk=None):
        """
        Get all lines for a specific journal entry.
        """
        journal_entry = self.get_object()
        lines = journal_entry.lines.all()
        serializer = JournalEntryLineSerializer(lines, many=True)
        return Response(serializer.data)

class JournalEntryLineViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on JournalEntryLine.
    """
    queryset = JournalEntryLine.objects.all()
    serializer_class = JournalEntryLineSerializer
    permission_classes = [IsAccountantOrReadOnly]