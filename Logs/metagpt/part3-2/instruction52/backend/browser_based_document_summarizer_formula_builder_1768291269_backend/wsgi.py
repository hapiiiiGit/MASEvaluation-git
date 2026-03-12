"""
WSGI config for browser_based_document_summarizer_formula_builder_1768291269_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'browser_based_document_summarizer_formula_builder_1768291269_backend.settings')

application = get_wsgi_application()
