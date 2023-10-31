from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from PyPDF2 import PdfReader


@api_view(['POST'])
@permission_classes([AllowAny])
def extract_pdf_text(request):
    if request.FILES.get('pdf_file') is None:
        return Response({'error': 'PDF file not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    pdf_file = request.FILES.get('pdf_file')
    try:
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)

        extracted_text = ''
        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            extracted_text += page.extract_text()

        return Response({'extracted_text': extracted_text})
    except Exception as e:
        return Response({'error': 'Unable to extract text from PDF.'}, status=status.HTTP_400_BAD_REQUEST)
