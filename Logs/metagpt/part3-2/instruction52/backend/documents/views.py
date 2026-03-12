from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Document
from .serializers import DocumentSerializer
from summaries.models import Summary
from summaries.serializers import SummarySerializer

import os
from django.conf import settings

# For document parsing
import PyPDF2
import docx

class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Document objects.
    Supports upload, list, retrieve, delete, and summary generation.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return documents belonging to the authenticated user
        return Document.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Handles uploading multiple documents.
        """
        files = request.FILES.getlist('files')
        if not files:
            return Response({'detail': 'No files provided.'}, status=status.HTTP_400_BAD_REQUEST)

        created_docs = []
        for file in files:
            filename = file.name
            file_type = self._get_file_type(filename)
            content = self._parse_file(file, file_type)
            document = Document.objects.create(
                user=request.user,
                filename=filename,
                file_type=file_type,
                content=content
            )
            created_docs.append(document)

        serializer = self.get_serializer(created_docs, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='summary')
    def summary(self, request, pk=None):
        """
        Generates or retrieves a summary for the document.
        """
        document = self.get_object()
        summary = Summary.objects.filter(document=document, user=request.user).first()
        if not summary:
            # Generate summary using the model's generate method
            summary_text = Summary().generate(document)
            summary = Summary.objects.create(
                document=document,
                user=request.user,
                summary_text=summary_text
            )
        serializer = SummarySerializer(summary)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def _get_file_type(self, filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.doc', '.docx']:
            return 'docx'
        elif ext == '.txt':
            return 'txt'
        else:
            return 'unknown'

    def _parse_file(self, file, file_type):
        """
        Parses the uploaded file and returns its text content.
        """
        try:
            if file_type == 'pdf':
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
            elif file_type == 'docx':
                doc = docx.Document(file)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text
            elif file_type == 'txt':
                return file.read().decode('utf-8')
            else:
                return ""
        except Exception as e:
            return f"Error parsing file: {e}"