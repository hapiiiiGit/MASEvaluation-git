from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Summary
from .serializers import SummarySerializer
from documents.models import Document

class SummaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Summary objects.
    Supports listing, retrieving, and deleting summaries for the authenticated user.
    Also supports generating a summary for a document.
    """
    queryset = Summary.objects.all()
    serializer_class = SummarySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return summaries belonging to the authenticated user
        return Summary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'], url_path='generate')
    def generate_summary(self, request):
        """
        Generates a summary for a given document.
        Expects 'document_id' in the request data.
        """
        document_id = request.data.get('document_id')
        if not document_id:
            return Response({'detail': 'document_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        document = get_object_or_404(Document, pk=document_id, user=request.user)
        # Check if summary already exists
        summary = Summary.objects.filter(document=document, user=request.user).first()
        if not summary:
            summary_text = Summary().generate(document)
            summary = Summary.objects.create(
                document=document,
                user=request.user,
                summary_text=summary_text
            )
        serializer = self.get_serializer(summary)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
        Deletes a summary.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)