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


class UserProfile(models.Model):
    user = models.ForeignKey(UserAccount, related_name='profile', on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.URLField(max_length=200, blank=True)
    phone_numbers = models.JSONField(blank=True, null=True)
    social_media = models.JSONField(blank=True, null=True)

    experience = models.ForeignKey('Experience', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    education = models.ForeignKey('Education', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    skill = models.ForeignKey('Skill', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    language = models.ForeignKey('Language', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    interest = models.ForeignKey('Interest', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    project = models.ForeignKey('Project', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    certification = models.ForeignKey('Certification', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    publication = models.ForeignKey('Publication', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    reference = models.ForeignKey('Reference', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    hobby = models.ForeignKey('Hobby', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)
    achievement = models.ForeignKey('Achievement', related_name='profile', on_delete=models.CASCADE, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


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
    proficiency = models.CharField(max_length=50)


class Language(models.Model):
    language = models.CharField(max_length=100)
    proficiency = models.CharField(max_length=50)


class Interest(models.Model):
    name = models.CharField(max_length=100)


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)


class Certification(models.Model):
    name = models.CharField(max_length=100)
    authority = models.CharField(max_length=100)
    date = models.DateField()


class Publication(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()


class Reference(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()


class Hobby(models.Model):
    name = models.CharField(max_length=100)


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
