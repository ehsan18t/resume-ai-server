import json

from django.conf import settings
from djoser.social.views import ProviderAuthView
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from users.models import *
from users.permissions import *
from users.serializers import *

from PyPDF2 import PdfReader
import google.generativeai as genai


class CustomProviderAuthView(ProviderAuthView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 201:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )
            response.set_cookie(
                'refresh',
                refresh_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token:
            request.data['refresh'] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access_token = response.data.get('access')

            response.set_cookie(
                'access',
                access_token,
                max_age=settings.AUTH_COOKIE_MAX_AGE,
                path=settings.AUTH_COOKIE_PATH,
                secure=settings.AUTH_COOKIE_SECURE,
                httponly=settings.AUTH_COOKIE_HTTP_ONLY,
                samesite=settings.AUTH_COOKIE_SAMESITE
            )

        return response


class CustomTokenVerifyView(TokenVerifyView):
    def post(self, request, *args, **kwargs):
        access_token = request.COOKIES.get('access')

        if access_token:
            request.data['token'] = access_token

        return super().post(request, *args, **kwargs)


class LogoutView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access')
        response.delete_cookie('refresh')

        return response


@api_view(['GET'])
@permission_classes([AdminToStudent])
def get_user_by_id(request):
    user_id = request.GET.get('user_id')
    user = UserAccount.objects.get(id=user_id)
    serializer = UserAccountSerializer(user, many=False)

    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def pdf_to_profile(request):
    global json_obj
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

        genai.configure(api_key="AIzaSyDx12uRNsU7-9_KJoC4vknansZxLzWcnkw")

        # Set up the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]

        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                      generation_config=generation_config,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[
        ])

        response = convo.send_message(f"""
        {extracted_text}
        can you organize this cv in json format for the following models
        
        # Main model
        class UserProfile(models.Model):
            user = models.ForeignKey(UserAccount, related_name='profile', on_delete=models.CASCADE)
            bio = models.TextField(max_length=500, blank=True)
            location = models.CharField(max_length=30, blank=True)
            birth_date = models.DateField(null=True, blank=True)
            website = models.URLField(max_length=200, blank=True)
            phone_numbers = models.JSONField(blank=True)
            social_media = models.JSONField(blank=True)
            
            # Models used in UserProfile
            experience = models.ForeignKey('Experience', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            education = models.ForeignKey('Education', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            skill = models.ForeignKey('Skill', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            language = models.ForeignKey('Language', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            interest = models.ForeignKey('Interest', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            project = models.ForeignKey('Project', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            certification = models.ForeignKey('Certification', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            publication = models.ForeignKey('Publication', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            reference = models.ForeignKey('Reference', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            hobby = models.ForeignKey('Hobby', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
            achievement = models.ForeignKey('Achievement', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
        
            created_at = models.DateTimeField(auto_now_add=True)
            updated_at = models.DateTimeField(auto_now=True)
        
        
        class Experience(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='experiences', on_delete=models.CASCADE)
            title = models.CharField(max_length=100)
            description = models.TextField()
            start_date = models.DateField()
            end_date = models.DateField(null=True, blank=True)
        
        
        class Education(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='educations', on_delete=models.CASCADE)
            institution = models.CharField(max_length=100)
            degree = models.CharField(max_length=100)
            field_of_study = models.CharField(max_length=100)
            start_date = models.DateField()
            end_date = models.DateField(null=True, blank=True)
        
        
        class Skill(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='skills', on_delete=models.CASCADE)
            name = models.CharField(max_length=100)
            proficiency = models.CharField(max_length=50)
        
        
        class Language(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='languages', on_delete=models.CASCADE)
            language = models.CharField(max_length=100)
            proficiency = models.CharField(max_length=50)
        
        
        class Interest(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='interests', on_delete=models.CASCADE)
            name = models.CharField(max_length=100)
        
        
        class Project(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='projects', on_delete=models.CASCADE)
            name = models.CharField(max_length=100)
            description = models.TextField()
            start_date = models.DateField()
            end_date = models.DateField(null=True, blank=True)
        
        
        class Certification(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='certifications', on_delete=models.CASCADE)
            name = models.CharField(max_length=100)
            authority = models.CharField(max_length=100)
            date = models.DateField()
        
        
        class Publication(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='publications', on_delete=models.CASCADE)
            title = models.CharField(max_length=200)
            description = models.TextField()
            date = models.DateField()
        
        
        class Reference(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='references', on_delete=models.CASCADE)
            name = models.CharField(max_length=100)
            email = models.EmailField()
        
        
        class Hobby(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='hobbies', on_delete=models.CASCADE)
            name = models.CharField(max_length=100)
        
        
        class Achievement(models.Model):
            user_profile = models.ForeignKey(UserProfile, related_name='achievements', on_delete=models.CASCADE)
            name = models.CharField(max_length=100)
            date = models.DateField()

        """)

        # Remove leading/trailing whitespace and replace newlines with commas
        json_data = response.text.strip()

        # save data to database
        try:
            json_obj = json.loads(json_data)
            # print
            print(json_obj[0])

            serializer = UserProfileSerializer(data=json_obj[0])
            if serializer.is_valid():
                profile = serializer.save()
                print('Profile created successfully!')
                profile_serializer = UserProfileSerializer(profile, many=False)
            else:
                print(serializer.errors)
        except Exception as e:
            print(f"Error decoding JSON: {e}")

        return Response({'json_data': json_obj[0]}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'error': "Some Error Has Occurred!"}, status=status.HTTP_400_BAD_REQUEST)
