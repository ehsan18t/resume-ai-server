from django.urls import path
from .views import *

urlpatterns = [
    path('extract-pdf-text/', extract_pdf_text, name='extract_pdf_text'),
]
