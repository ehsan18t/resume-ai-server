from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from .models import *


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


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = '__all__'


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'


class HobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobby
        fields = '__all__'


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=UserAccount.objects.all())
    experiences = ExperienceSerializer(many=True)
    educations = EducationSerializer(many=True)
    skills = SkillSerializer(many=True)
    languages = LanguageSerializer(many=True)
    interests = InterestSerializer(many=True)
    projects = ProjectSerializer(many=True)
    certifications = CertificationSerializer(many=True)
    publications = PublicationSerializer(many=True)
    references = ReferenceSerializer(many=True)
    hobbies = HobbySerializer(many=True)
    achievements = AchievementSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

    @staticmethod
    def get_nested_data(validated_data):
        return {
            'experiences': validated_data.pop('experiences', []),
            'educations': validated_data.pop('educations', []),
            'skills': validated_data.pop('skills', []),
            'languages': validated_data.pop('languages', []),
            'interests': validated_data.pop('interests', []),
            'projects': validated_data.pop('projects', []),
            'certifications': validated_data.pop('certifications', []),
            'publications': validated_data.pop('publications', []),
            'references': validated_data.pop('references', []),
            'hobbies': validated_data.pop('hobbies', []),
            'achievements': validated_data.pop('achievements', []),
        }

    def create(self, validated_data):
        nested_data = self.get_nested_data(validated_data)

        user_profile = UserProfile.objects.create(**validated_data)

        for key, value in nested_data.items():
            for item in value:
                item['user_profile'] = user_profile
                globals()[f"{key[:-1].capitalize()}Serializer"].create(item)

        return user_profile

    def update(self, instance, validated_data):
        nested_data = self.get_nested_data(validated_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for key, value in nested_data.items():
            model = globals()[f"{key[:-1].capitalize()}"]
            model.objects.filter(user_profile=instance).delete()
            for item in value:
                item['user_profile'] = instance
                globals()[f"{key[:-1].capitalize()}Serializer"].create(item)

        return instance
