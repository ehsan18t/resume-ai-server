from rest_framework import serializers

from post.serializers import PostSerializer
from users.serializers import UserAccountSerializerMin, UserProfileSerializer
from .models import *


class AppliedCandidatesSerializer(serializers.ModelSerializer):
    user = UserAccountSerializerMin()
    post = PostSerializer()

    class Meta:
        model = AppliedCandidates
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    cv = AppliedCandidatesSerializer()

    class Meta:
        model = Feedback
        fields = '__all__'
