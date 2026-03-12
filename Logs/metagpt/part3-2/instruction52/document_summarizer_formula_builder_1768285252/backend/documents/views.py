from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Document
from .serializers import DocumentSerializer
from django.conf import settings

import os
import tempfile

# Document parsing libraries
import PyPDF2
import docx

# Summarization libraries
import spacy

# Load spaCy model for summarization (English)
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def summarize_text(text, max_sentences=3):
    # Simple extractive summarization using spaCy sentences
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 0]
    return " ".join(sentences[:max_sentences]) if sentences else text[:200]

class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for uploading, listing, retrieving, and deleting documents.
    Includes automatic summarization on upload.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        # Only return documents owned by the current user
        return Document.objects.filter(owner=self.request.user).order_by('-upload_time')

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get('file')
        if not uploaded_file:
            raise ValueError("No file uploaded.")

        file_name = uploaded_file.name
        file_type = None
        content = ""

        # Save uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Determine file type and extract content
        ext = os.path.splitext(file_name)[1].lower()
        if ext == ".pdf":
            file_type = "pdf"
            content = extract_text_from_pdf(tmp_path)
        elif ext == ".docx":
            file_type = "docx"
            content = extract_text_from_docx(tmp_path)
        elif ext == ".txt":
            file_type = "txt"
            with open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            os.unlink(tmp_path)
            raise ValueError("Unsupported file type. Only PDF, DOCX, and TXT are allowed.")

        os.unlink(tmp_path)

        # Generate summary
        summary = summarize_text(content)

        serializer.save(
            owner=self.request.user,
            file_name=file_name,
            file_type=file_type,
            content=content,
            summary=summary
        )

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def summary(self, request, pk=None):
        """
        Custom action to retrieve the summary of a document.
        """
        document = get_object_or_404(Document, pk=pk, owner=request.user)
        return Response({'summary': document.summary}, status=status.HTTP_200_OK)