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

    def create(self, validated_data):
        experiences_data = validated_data.pop('experiences')
        educations_data = validated_data.pop('educations')
        skills_data = validated_data.pop('skills')
        languages_data = validated_data.pop('languages')
        interests_data = validated_data.pop('interests')
        projects_data = validated_data.pop('projects')
        certifications_data = validated_data.pop('certifications')
        publications_data = validated_data.pop('publications')
        references_data = validated_data.pop('references')
        hobbies_data = validated_data.pop('hobbies')
        achievements_data = validated_data.pop('achievements')

        user_profile = UserProfile.objects.create(**validated_data)

        for experience_data in experiences_data:
            Experience.objects.create(**experience_data)

        for education_data in educations_data:
            Education.objects.create(**education_data)

        for skill_data in skills_data:
            Skill.objects.create(**skill_data)

        for language_data in languages_data:
            Language.objects.create(**language_data)

        for interest_data in interests_data:
            Interest.objects.create(**interest_data)

        for project_data in projects_data:
            Project.objects.create(**project_data)

        for certification_data in certifications_data:
            Certification.objects.create(**certification_data)

        for publication_data in publications_data:
            Publication.objects.create(**publication_data)

        for reference_data in references_data:
            Reference.objects.create(**reference_data)

        for hobby_data in hobbies_data:
            Hobby.objects.create(**hobby_data)

        for achievement_data in achievements_data:
            Achievement.objects.create(**achievement_data)

        return user_profile

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['experiences'] = ExperienceSerializer(instance.experiences.all(), many=True).data
        data['educations'] = EducationSerializer(instance.educations.all(), many=True).data
        data['skills'] = SkillSerializer(instance.skills.all(), many=True).data
        data['languages'] = LanguageSerializer(instance.languages.all(), many=True).data
        data['interests'] = InterestSerializer(instance.interests.all(), many=True).data
        data['projects'] = ProjectSerializer(instance.projects.all(), many=True).data
        data['certifications'] = CertificationSerializer(instance.certifications.all(), many=True).data
        data['publications'] = PublicationSerializer(instance.publications.all(), many=True).data
        data['references'] = ReferenceSerializer(instance.references.all(), many=True).data
        data['hobbies'] = HobbySerializer(instance.hobbies.all(), many=True).data
        data['achievements'] = AchievementSerializer(instance.achievements.all(), many=True).data
        return data
