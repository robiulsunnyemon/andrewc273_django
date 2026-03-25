from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from datetime import timedelta
import random


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)
    

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)

    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_exp = models.DateTimeField(blank=True, null=True)
    otp_verified = models.BooleanField(default=False)


    USERNAME_FIELD = "email"
    objects = UserManager()

    def generate_otp(self, test_otp=None):
        if test_otp:
            self.otp = str(test_otp)
        else:
            self.otp = str(random.randint(1000, 9999))
        self.otp_exp = timezone.now() + timedelta(minutes=10)
        self.otp_verified = False
        self.save()
        # self.otp = str(random.randint(1000, 9999))  # Generate 4-digit OTP
        # self.otp_exp = timezone.now() + timedelta(minutes=10)
        # self.otp_verified = False
        # self.save()
     

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    name = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)

    total_letters = models.PositiveIntegerField(default=0)
    total_posts = models.PositiveIntegerField(default=0)
    has_podcast_story = models.BooleanField(default=False, help_text="Featured in Podcast/Story for Star badge")

    def __str__(self):
        return f"Profile({self.user.email})"


class SocialLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="social_link")
    facebook = models.URLField(blank=True)
    x = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    truth = models.URLField(blank=True)

    def __str__(self):
        return f"SocialLink({self.user.email})"
    
    @property
    def connected_count(self):
        """Koti social link field-e data ache seta count korbe"""
        links = [self.facebook, self.x, self.instagram, self.youtube, self.truth]
        return sum(1 for link in links if link)

