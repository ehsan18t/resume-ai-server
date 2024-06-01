from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from datetime import timedelta

from django.utils import timezone
from .models import *




def gen_formatted_time(obj):
    now = timezone.now()
    time_diff = now - obj.created_at

    if time_diff < timedelta(minutes=59):
        mins = time_diff.seconds // 60
        return f"{mins}m ago" if mins > 0 else "Just now"
    elif time_diff < timedelta(hours=24):
        hours = time_diff.seconds // 3600
        return f"{hours}h ago" if hours > 0 else "Just now"
    elif time_diff < timedelta(days=3):
        days = time_diff.days
        return f"{days}d ago"
    else:
        return obj.created_at.strftime('%b %d, %Y')


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class CustomUserCreateSerializerRetype(CustomUserCreateSerializer):
    class Meta(CustomUserCreateSerializer.Meta):
        fields = ('first_name', 'last_name', 'username', 'email', 'password')


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'profile_picture', 'user_type']


class UserAccountSerializerMin(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'first_name', 'last_name', 'username']


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserAccount.objects.all())

    class Meta:
        model = UserProfile
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    formatted_time = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = '__all__'

    def get_formatted_time(self, obj):
        return gen_formatted_time(obj)
