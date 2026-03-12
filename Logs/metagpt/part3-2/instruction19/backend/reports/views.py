from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import FinancialReport
from .serializers import FinancialReportSerializer

class IsFinancialControllerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow financial controllers or admins to generate reports.
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
        return role.name in ['Financial Controller', 'Admin']

class FinancialReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for CRUD operations on FinancialReport.
    """
    queryset = FinancialReport.objects.all().order_by('-generated_at')
    serializer_class = FinancialReportSerializer
    permission_classes = [IsFinancialControllerOrAdmin]

    def perform_create(self, serializer):
        serializer.save(generated_by=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def balance_sheet(self, request):
        """
        Generate and return a balance sheet report.
        """
        # In a real system, you would aggregate data from the general ledger here.
        # For demonstration, we return a dummy structure.
        data = {
            "assets": 100000,
            "liabilities": 40000,
            "equity": 60000,
        }
        report = FinancialReport.objects.create(
            type='BALANCE_SHEET',
            parameters=request.query_params.dict(),
            generated_by=request.user,
            data=data
        )
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def income_statement(self, request):
        """
        Generate and return an income statement report.
        """
        # In a real system, you would aggregate data from the general ledger here.
        # For demonstration, we return a dummy structure.
        data = {
            "revenue": 150000,
            "expenses": 90000,
            "net_income": 60000,
        }
        report = FinancialReport.objects.create(
            type='INCOME_STATEMENT',
            parameters=request.query_params.dict(),
            generated_by=request.user,
            data=data
        )
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def cash_flow(self, request):
        """
        Generate and return a cash flow report.
        """
        # In a real system, you would aggregate data from the general ledger here.
        # For demonstration, we return a dummy structure.
        data = {
            "operating_activities": 50000,
            "investing_activities": -10000,
            "financing_activities": 20000,
            "net_cash_flow": 60000,
        }
        report = FinancialReport.objects.create(
            type='CASH_FLOW',
            parameters=request.query_params.dict(),
            generated_by=request.user,
            data=data
        )
        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)