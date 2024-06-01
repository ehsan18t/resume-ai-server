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

        # Create user profile
        UserProfile.objects.create(user=user)

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
    title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    website = models.CharField(max_length=200, blank=True, null=True)
    phone_numbers = models.JSONField(blank=True, null=True)
    social_media = models.JSONField(blank=True, null=True)

    experiences = models.JSONField(blank=True, null=True)
    educations = models.JSONField(blank=True, null=True)
    skills = models.JSONField(blank=True, null=True)
    languages = models.JSONField(blank=True, null=True)
    interests = models.JSONField(blank=True, null=True)
    projects = models.JSONField(blank=True, null=True)
    certifications = models.JSONField(blank=True, null=True)
    publications = models.JSONField(blank=True, null=True)
    references = models.JSONField(blank=True, null=True)
    hobbies = models.JSONField(blank=True, null=True)
    achievements = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Notification(models.Model):
    user = models.ForeignKey(UserAccount, related_name='user', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField(max_length=500)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
