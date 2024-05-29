from rest_framework import serializers

from .models import *


class AppliedCandidatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppliedCandidates
        fields = '__all__'
