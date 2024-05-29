from rest_framework import serializers

from users.serializers import UserAccountSerializerMin, UserProfileSerializer
from .models import *


class AppliedCandidatesSerializer(serializers.ModelSerializer):
    user = UserAccountSerializerMin()
    profile = UserProfileSerializer()

    class Meta:
        model = AppliedCandidates
        fields = '__all__'
