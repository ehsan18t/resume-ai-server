from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

import users.serializers
from cv.models import AppliedCandidates
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


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


class PostSerializer(serializers.ModelSerializer):
    user = users.serializers.UserAccountSerializerMin()
    formatted_time = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = '__all__'

    def get_formatted_time(self, obj):
        return gen_formatted_time(obj)
