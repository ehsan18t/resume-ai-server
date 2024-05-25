from enum import Enum

from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserType(Enum):
    SU = 0
    ADMIN = 1
    MOD = 2
    REPRESENTATIVE = 3
    USER = 4


class UserAccountManager(BaseUserManager):
    def create_superuser(self, email, password, username, **other_fields):
        # Creating Normal User
        user = self.create_user(
            email,
            password,
            username,
            **other_fields
        )

        # Set admin permissions
        user.user_type = 0
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True

        user.save()
        return user

    def create_user(self, email, password, username, **other_fields):
        # Validations
        if not email:
            raise ValueError('You must provide an email address')
        if not username:
            raise ValueError('You must provide a username')

        # Normalizations
        email = email.lower()
        username = username.lower()

        # User creation 
        user = self.model(
            email=email,
            username=username,
            **other_fields
        )

        user.set_password(password)
        user.save()
        return user


class UserAccount(AbstractUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    profile_picture = models.FileField(upload_to='profile_pictures/', default='profile_pictures/avatar-male.png')
    start_date = models.DateTimeField(auto_now_add=True)

    # For database admin (in server)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USER_TYPE_CHOICES = [
        (UserType.SU.value, 'Super Admin'),
        (UserType.ADMIN.value, 'Admin'),
        (UserType.MOD.value, 'Moderator'),
        (UserType.REPRESENTATIVE.value, 'Representative'),
        (UserType.USER.value, 'User'),
    ]

    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=UserType.USER.value)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    objects = UserAccountManager()

    def __str__(self):
        return f'{self.first_name} {self.last_name} [{self.username}]'


# Main model
class UserProfile(models.Model):
    user = models.OneToOneField(UserAccount, related_name='profile', on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.CharField(max_length=200, blank=True, null=True)
    phone_numbers = models.JSONField(blank=True, null=True)
    social_media = models.JSONField(blank=True, null=True)

    experiences = models.ManyToManyField('Experience', related_name='profiles', blank=True)
    educations = models.ManyToManyField('Education', related_name='profiles', blank=True)
    skills = models.ManyToManyField('Skill', related_name='profiles', blank=True)
    languages = models.ManyToManyField('Language', related_name='profiles', blank=True)
    interests = models.ManyToManyField('Interest', related_name='profiles', blank=True)
    projects = models.ManyToManyField('Project', related_name='profiles', blank=True)
    certifications = models.ManyToManyField('Certification', related_name='profiles', blank=True)
    publications = models.ManyToManyField('Publication', related_name='profiles', blank=True)
    references = models.ManyToManyField('Reference', related_name='profiles', blank=True)
    hobbies = models.ManyToManyField('Hobby', related_name='profiles', blank=True)
    achievements = models.ManyToManyField('Achievement', related_name='profiles', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Models used in UserProfile
class Experience(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class Education(models.Model):
    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class Skill(models.Model):
    name = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=50, blank=True, null=True)


class Language(models.Model):
    language = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=50, blank=True, null=True)


class Interest(models.Model):
    name = models.CharField(max_length=100)


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)


class Certification(models.Model):
    name = models.CharField(max_length=100)
    authority = models.CharField(max_length=100, null=True, blank=True)
    date = models.DateField(null=True, blank=True)


class Publication(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)


class Reference(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)


class Hobby(models.Model):
    name = models.CharField(max_length=100)


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(null=True, blank=True)
