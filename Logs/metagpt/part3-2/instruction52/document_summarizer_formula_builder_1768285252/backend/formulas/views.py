from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Formula
from .serializers import FormulaSerializer
from django.contrib.auth.models import User
import numexpr

class FormulaViewSet(viewsets.ModelViewSet):
    """
    API endpoint for creating, listing, retrieving, updating, deleting, sharing, and evaluating formulas.
    """
    queryset = Formula.objects.all()
    serializer_class = FormulaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return formulas owned by the current user or shared with them
        return Formula.objects.filter(
            models.Q(owner=self.request.user) | models.Q(shared_with=self.request.user)
        ).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def share(self, request, pk=None):
        """
        Custom action to share a formula with other users.
        Expects a list of user IDs in 'user_ids'.
        """
        formula = get_object_or_404(Formula, pk=pk, owner=request.user)
        user_ids = request.data.get('user_ids', [])
        if not isinstance(user_ids, list):
            return Response({'error': 'user_ids must be a list.'}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=user_ids)
        formula.shared_with.set(users)
        formula.save()
        return Response({'status': 'shared', 'shared_with': [u.username for u in users]}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def calculate(self, request, pk=None):
        """
        Custom action to evaluate a formula with provided inputs.
        Expects a dict of variable values in 'inputs'.
        """
        formula = get_object_or_404(Formula, pk=pk)
        # Only allow calculation if user is owner or shared_with
        if formula.owner != request.user and request.user not in formula.shared_with.all():
            return Response({'error': 'You do not have access to this formula.'}, status=status.HTTP_403_FORBIDDEN)

        inputs = request.data.get('inputs', {})
        if not isinstance(inputs, dict):
            return Response({'error': 'inputs must be a dict.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate that all required variables are provided
        required_vars = list(formula.variables.keys())
        missing_vars = [var for var in required_vars if var not in inputs]
        if missing_vars:
            return Response({'error': f'Missing variables: {missing_vars}'}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare the expression and evaluate safely
        try:
            # numexpr evaluates mathematical expressions safely
            result = numexpr.evaluate(formula.expression, local_dict=inputs)
            result = float(result)
        except Exception as e:
            return Response({'error': f'Error evaluating formula: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'result': result}, status=status.HTTP_200_OK)