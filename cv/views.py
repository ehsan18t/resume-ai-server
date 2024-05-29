from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.models import UserAccount
from .models import *
from post.models import Post
from .serializers import *


@api_view(['POST'])
@permission_classes([AllowAny])
def apply_job(request):
    try:
        post = Post.objects.get(id=request.data.get('post'))
        user = request.user
        cv = request.data.get('cv')

        applied = AppliedCandidates.objects.create(post=post, user=user, cv=cv)
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
