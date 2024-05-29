from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import *
from .serializers import *


@api_view(['POST'])
@permission_classes([AllowAny])
def create_post(request):
    try:
        user = request.user
        content = request.data.get('content')
        print(content)
        is_job_circular = True if request.data.get('is_job_circular') == 1 else False
        print(is_job_circular)
        category = Category.objects.get(slung=request.data.get('category'))

        post = Post.objects.create(user=user, content=content, is_job_circular=is_job_circular, category=category)
        post.save()
        serialized = PostSerializer(post)

        return Response({'msg': 'Post created successfully!', 'post': serialized.data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'msg': 'Failed to create post!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_user_posts(request):
    try:
        user = request.user
        posts = Post.objects.filter(user=user, category=None)
        serialized = PostSerializer(posts, many=True)

        return Response({'posts': serialized.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'msg': 'Failed to fetch posts!'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_category(request):
    try:
        cat = request.data.get('category')
        category = Category.objects.create(name=cat)
        category.save()
        serialized = CategorySerializer(category)

        return Response({'msg': 'Category created successfully!', 'category': serialized.data},
                        status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'msg': 'Failed to create category!'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_list(request):
    try:
        categories = Category.objects.all()
        serialized = CategorySerializer(categories, many=True)

        return Response({'categories': serialized.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'msg': 'Failed to fetch categories!'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_category_posts(request):
    try:
        slung = request.GET.get('slung')
        category = Category.objects.get(slung=slung)
        posts = Post.objects.filter(category=category)
        serialized = PostSerializer(posts, many=True)

        return Response({'posts': serialized.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'msg': 'Failed to find posts!'}, status=status.HTTP_404_NOT_FOUND)
