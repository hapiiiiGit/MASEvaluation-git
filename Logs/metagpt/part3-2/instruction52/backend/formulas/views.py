from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Formula, FormulaResult
from .serializers import FormulaSerializer, FormulaResultSerializer

class FormulaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Formula objects.
    Supports creating, listing, retrieving, updating, and deleting formulas for the authenticated user.
    Also supports evaluating formulas.
    """
    queryset = Formula.objects.all()
    serializer_class = FormulaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return formulas belonging to the authenticated user
        return Formula.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='evaluate')
    def evaluate_formula(self, request, pk=None):
        """
        Evaluates the formula with provided input_data.
        Expects 'input_data' (dict) in the request data.
        Stores and returns the result.
        """
        formula = self.get_object()
        input_data = request.data.get('input_data')
        if not isinstance(input_data, dict):
            return Response({'detail': 'input_data must be a dictionary.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result_value = formula.evaluate(input_data)
        except Exception as e:
            return Response({'detail': f'Error evaluating formula: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        formula_result = FormulaResult.objects.create(
            formula=formula,
            user=request.user,
            input_data=input_data,
            result=result_value
        )
        serializer = FormulaResultSerializer(formula_result)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='saved')
    def saved_formulas(self, request):
        """
        Returns a list of saved formulas for the authenticated user.
        """
        formulas = Formula.objects.filter(user=request.user)
        serializer = self.get_serializer(formulas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FormulaResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing FormulaResult objects.
    Supports listing and retrieving formula results for the authenticated user.
    """
    queryset = FormulaResult.objects.all()
    serializer_class = FormulaResultSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return formula results belonging to the authenticated user
        return FormulaResult.objects.filter(user=self.request.user)