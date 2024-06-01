from datetime import datetime, timezone
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


def get_response(extracted_text):
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
        title = models.CharField(max_length=100, blank=True, null=True, related_name='profession/job title')
        # generate bio if not exist
        bio = models.TextField(max_length=500, blank=True, null=True)
        location = models.CharField(max_length=100, blank=True, null=True)
        birth_date = models.DateField(null=True, blank=True, null=True)
        website = models.URLField(max_length=200, blank=True, null=True)
        phone_numbers = models.JSONField(blank=True)
        social_media = models.OneToOneField('SocialMedia', blank=True, null=True)

        experiences = models.ManyToManyField('Experience', blank=True)
        educations = models.ManyToManyField('Education', blank=True)
        skills = models.ManyToManyField('Skill', blank=True)
        languages = models.ManyToManyField('Language', blank=True)
        interests = models.ManyToManyField('Interest', blank=True)
        projects = models.ManyToManyField('Project', blank=True)
        certifications = models.ManyToManyField('Certification', blank=True)
        publications = models.ManyToManyField('Publication', blank=True)
        references = models.ManyToManyField('Reference', blank=True)
        hobbies = models.ManyToManyField('Hobby', blank=True)
        achievements = models.ManyToManyField('Achievement', blank=True)

        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
    
    
    # Models used in UserProfile
    class SocialMedia(models.Model):
        github = models.CharField(max_length=100, related_name='github username')
        linkedin = models.CharField(max_length=100, related_name='linkedin username')
        twitter = models.CharField(max_length=100, related_name='twitter username')
        facebook = models.CharField(max_length=100, related_name='facebook username')
        email = models.CharField(max_length=100, related_name='email address')

    class Experience(models.Model):
        title = models.CharField(max_length=100)
        description = models.TextField()
        start_date = models.DateField()
        end_date = models.DateField(null=True, blank=True)
    
    
    class Education(models.Model):
        institution = models.CharField(max_length=100)
        degree = models.CharField(max_length=100)
        cgpa = models.FloatField(null=True, blank=True)
        field_of_study = models.CharField(max_length=100)
        start_date = models.DateField()
        end_date = models.DateField(null=True, blank=True)
    
    
    class Skill(models.Model):
        name = models.CharField(max_length=100)
        proficiency = models.CharField(max_length=50)
    
    
    class Language(models.Model):
        language = models.CharField(max_length=100)
        proficiency = models.CharField(max_length=50)
    
    
    class Interest(models.Model):
        name = models.CharField(max_length=100)
    

    class Project(models.Model):
        name = models.CharField(max_length=100)
        description = models.TextField()
        tags = models.JSONField(null=True, blank=True)
        start_date = models.DateField()
        end_date = models.DateField(null=True, blank=True)
    
    
    class Certification(models.Model):
        name = models.CharField(max_length=100)
        authority = models.CharField(max_length=100)
        description = models.TextField(null=True, blank=True)
        date = models.DateField(null=True, blank=True)
    
    
    class Publication(models.Model):
        title = models.CharField(max_length=200)
        description = models.TextField(null=True, blank=True)
        date = models.DateField(null=True, blank=True)
    
    
    class Reference(models.Model):
        name = models.CharField(max_length=100)
        designation = models.CharField(max_length=100, null=True, blank=True)
        email = models.EmailField(null=True, blank=True)
        phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    
    class Hobby(models.Model):
        name = models.CharField(max_length=100)
    

    class Achievement(models.Model):
        name = models.CharField(max_length=100)
        description = models.TextField(null=True, blank=True)
        date = models.DateField(null=True, blank=True)

    """)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[
    ])

    return response.text.strip()


def get_fake_response(extracted_text):
    return "{\"user\": \"null\", \"bio\": \"A passionate developer, competitive programmer and quick learner. Love to code and learn new things.\", \"location\": \"Rainbow Vally, Fasertek Road, Vatara Thana, Dhaka Bangladesh\", \"birth_date\": null, \"website\": \"beehsan.pages.dev\", \"phone_numbers\": \"[\\\"+8801641723411\\\"]\", \"social_media\": \"{\\\"linkedin\\\": \\\"/linkedinehsan18t\\\", \\\"github\\\": \\\"/githubehsan18t\\\"}\", \"experiences\": [{\"title\": \"OS Modder\", \"description\": \"Modify Windows OS with many tweaks and patches\", \"start_date\": \"2018-05-01\", \"end_date\": null}, {\"title\": \"Android ROM Developer\", \"description\": \"AOSP Custom ROM\\nReverse Engineered OEM ROM\", \"start_date\": \"2018-05-01\", \"end_date\": \"2019-12-31\"}], \"educations\": [{\"institution\": \"United International University\", \"degree\": \"B.Sc in Computer Science and Engineering\", \"field_of_study\": \"Computer Science and Engineering\", \"start_date\": \"2020-01-01\", \"end_date\": null}], \"skills\": [{\"name\": \"Linux Bash Batch\", \"proficiency\": null}, {\"name\": \"Python\", \"proficiency\": null}, {\"name\": \"PHP\", \"proficiency\": null}, {\"name\": \"SQL\", \"proficiency\": null}, {\"name\": \"Googling\", \"proficiency\": null}, {\"name\": \"HTML\", \"proficiency\": null}, {\"name\": \"CSS\", \"proficiency\": null}, {\"name\": \"JavaScript\", \"proficiency\": null}, {\"name\": \"TailwindCSS\", \"proficiency\": null}, {\"name\": \"React\", \"proficiency\": null}, {\"name\": \"Svelte\", \"proficiency\": null}, {\"name\": \"C/C++\", \"proficiency\": null}, {\"name\": \"Java\", \"proficiency\": null}, {\"name\": \"Django\", \"proficiency\": null}, {\"name\": \"Git\", \"proficiency\": null}, {\"name\": \"GitHub\", \"proficiency\": null}, {\"name\": \"Github Action\", \"proficiency\": null}, {\"name\": \"Vim\", \"proficiency\": null}, {\"name\": \"Markdown\", \"proficiency\": null}, {\"name\": \"Figma\", \"proficiency\": null}, {\"name\": \"Jira\", \"proficiency\": null}, {\"name\": \"Scrum\", \"proficiency\": null}, {\"name\": \"Photoshop\", \"proficiency\": null}, {\"name\": \"Filmora\", \"proficiency\": null}, {\"name\": \"MS Office\", \"proficiency\": null}], \"languages\": [{\"language\": \"Bengali\", \"proficiency\": null}, {\"language\": \"English\", \"proficiency\": null}], \"interests\": [{\"name\": \"Development\"}, {\"name\": \"Cyber Security\"}, {\"name\": \"Reverse Engineering\"}], \"projects\": [{\"name\": \"Contest Reminder\", \"description\": \"An amazing automation tool to remind you about upcoming contests from various judge like CodeForces, CodeChef, Atcoder (user selected judges) etc. It doesn’t require any API key or login or any computer. It uses web scraping to get the data. Just setup and forget. Initially created with java, currently recreating with python.\", \"start_date\": null, \"end_date\": null}, {\"name\": \"Course Assistant\", \"description\": \"An allrounder helper for undergraduate student which solves real-life problems. It helps to manage course, assignments, exams, attendance, grades, etc. It also has a built-in timetable generator, attendance tracker, grade calculator, etc. Initially created with php, recently recreated with django.\", \"start_date\": null, \"end_date\": null}, {\"name\": \"MagicX Toolbox\", \"description\": \"A script based ultimate tool to control almost everything in windows.\", \"start_date\": null, \"end_date\": null}, {\"name\": \"Win10 Ultimate System Tweaks\", \"description\": \"A script/tool to make windows 10 better by adding useful features & tools, disabling useless services, turning off logging and sending data to third-party and removing garbage.\", \"start_date\": null, \"end_date\": null}], \"certifications\": [{\"name\": \"CCNA: Introduction to Networks\", \"authority\": \"CISCO\", \"date\": \"2023-03-01\"}], \"publications\": [], \"references\": [], \"hobbies\": [], \"achievements\": [{\"name\": \"UIU Project Show Champion Fall 2021\", \"date\": \"2021-12-01\"}], \"created_at\": \"null\", \"updated_at\": \"null\"}"


@api_view(['POST'])
@permission_classes([AllowAny])
def pdf_to_profile(request):
    if request.FILES.get('pdf_file') is None:
        return Response({'error': 'PDF file not provided.'}, status=status.HTTP_400_BAD_REQUEST)

    pdf_file = request.FILES.get('pdf_file')

    if request.user.id is None:
        return Response({'error': 'Anonymous request not allowed!'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user already have a profile
    profile = UserProfile.objects.get(user=request.user)
    if profile:
        print('Profile found for the user!')

    try:
        pdf_reader = PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)

        extracted_text = ''
        for page_number in range(num_pages):
            page = pdf_reader.pages[page_number]
            extracted_text += page.extract_text()

        # save data to database
        try:
            json_obj = json.loads(get_response(extracted_text))

            # Add the user information to the json_obj
            json_obj['user'] = request.user.id
            current_time_utc = datetime.now(timezone.utc)
            json_obj["created_at"] = current_time_utc
            json_obj["updated_at"] = current_time_utc

            serializer = UserProfileSerializer(data=json_obj, partial=True)

            print('serializer created')
            if serializer.is_valid():
                if profile:
                    # populate date from new serializer to old profile object
                    for key, value in serializer.validated_data.items():
                        setattr(profile, key, value)
                    profile.save()
                else:
                    profile = serializer.save()

                print('Profile created successfully!')
                profile_serializer = UserProfileSerializer(profile, many=False)
                return Response({'profile': profile_serializer.data}, status=status.HTTP_200_OK)
            else:
                print(serializer.errors)
        except Exception as e:
            print(f"Error decoding JSON: {e}")
        return Response({'error': "Some Error Has Occurred!"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'error': "Some Error Has Occurred!"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_profile_by_id(request):
    try:
        u = request.GET.get('u')

        if u.isdigit():
            user = UserAccount.objects.get(id=u)
        else:
            user = UserAccount.objects.get(username=u)

        user_serializer = UserAccountSerializer(user, many=False)
        try:
            profile = UserProfile.objects.get(user=user)
            profile_serializer = UserProfileSerializer(profile, many=False)
            return Response({'user': user_serializer.data, 'profile': profile_serializer.data},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'user': user_serializer.data, 'profile': {}}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Profile not found!'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_unread_notifications_count(request):
    try:
        user = request.user
        notifications = Notification.objects.filter(user=user, is_read=False)
        return Response({'count': notifications.count()}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_notification_list(request):
    user = request.user

    if user.id is None:
        return Response({'error': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)

    try:
        notifications = Notification.objects.filter(user=user).order_by('-created_at')

        for notification in notifications:
            if not notification.is_seen:
                notification.is_seen = True
                notification.save()
            elif notification.is_seen and not notification.is_read:
                notification.is_read = True
                notification.save()
            else:
                break

        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Unexpected Error!'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def clear_notifications(request):
    user = request.user

    if user.id is None:
        return Response({'error': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)

    try:
        notifications = Notification.objects.filter(user=user)
        for notification in notifications:
            notification.delete()

        return Response({'message': 'All notifications cleared!'}, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'error': 'Unexpected Error!'}, status=status.HTTP_404_NOT_FOUND)
