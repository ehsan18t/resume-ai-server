from post.models import Post
from .serializers import *
import json

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


from users.serializers import *

import google.generativeai as genai


@api_view(['POST'])
@permission_classes([AllowAny])
def apply_job(request):
    if not request.user.is_authenticated:
        return Response({'msg': 'User not authenticated!'}, status=status.HTTP_400_BAD_REQUEST)

    if request.data.get('post') is None:
        return Response({'msg': 'Post ID is required!'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        post = Post.objects.get(id=request.data.get('post'))
        user = request.user
        profile = UserProfile.objects.get(user=user)
        # cv = request.data.get('cv')

        applied = AppliedCandidates.objects.create(post=post, user=user, profile=profile)
        applied.save()

        return Response({'msg': 'Applied successfully!'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'msg': 'Failed to apply!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def change_cv_status(request):
    try:
        post = Post.objects.get(id=request.data.get('post'))
        user = UserAccount.objects.get(id=request.data.get('user'))
        s = request.data.get('status')

        cv = AppliedCandidates.objects.get(post=post, user=user)
        cv.status = s
        cv.save()

        Notification.objects.create(user=user, title=f"Your CV status has been updated to {s}")

        return Response({'msg': 'CV Status Changed Successfully!'}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'msg': 'Failed to change CV status!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cv_list(request):
    try:
        post = Post.objects.get(id=request.GET.get('post'))
        cvs = AppliedCandidates.objects.filter(post=post)
        serialized = AppliedCandidatesSerializer(cvs, many=True)

        return Response({'applications': serialized.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'msg': 'Failed to fetch categories!'}, status=status.HTTP_404_NOT_FOUND)


def request_summary(text):
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
    {text}

    can you summarize this cv section by section in a way that is smaller to read easier to understand the context and make sure to not miss out important informations and format in the following way and return valid json object?

    "summary":
        "experiences": string | null,
        "educations": string | null,
        "skills": string | null,
        "languages": string | null,
        "projects": string | null,
        "certifications": string | null,
        "publications": string | null,
        "references": string | null,
        "achievements": string | null

        if no info available for a section, return null
    """)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[
    ])

    return response.text.strip()


@api_view(['GET'])
@permission_classes([AllowAny])
def get_cv_summary(request):
    try:
        u = request.GET.get('u')

        if u.isdigit():
            user = UserAccount.objects.get(id=u)
        else:
            user = UserAccount.objects.get(username=u)

        profile = UserProfile.objects.get(user=user)
        profile_serializer = UserProfileSerializer(profile, many=False)

        # Convert the serializer data to JSON
        profile_json = json.dumps(profile_serializer.data)

        summary = json.loads(request_summary(profile_json))
        return Response({"profile": profile_serializer.data, "summary": summary}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Profile not found!'}, status=status.HTTP_404_NOT_FOUND)
