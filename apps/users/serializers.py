

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.exceptions import ValidationError
from .models import Profile, SocialLink
User = get_user_model()

from django.utils.timezone import now, timedelta
from django.conf import settings


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name  = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirm_password', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        # pop extra fields before creating user
        first_name = validated_data.pop('first_name', '')
        last_name  = validated_data.pop('last_name', '')
        validated_data.pop('confirm_password')

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )

       
        Profile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            name=f"{first_name} {last_name}".strip(),
        )
        SocialLink.objects.create(user=user)
        return user




class EmailVerificationSerializer(serializers.Serializer):
    """
    Verifies the signup OTP and activates the user account.
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        if not user.otp or user.otp != data["otp"]:
            raise serializers.ValidationError({"otp": "Invalid OTP."})
        if not user.otp_exp or user.otp_exp < now():
            raise serializers.ValidationError({"otp": "OTP expired."})

        # Activate and clear OTP on success
        user.is_active = True
        user.otp_verified = True
        user.otp = None
        user.otp_exp = None
        user.save()
        return data


class ResendVerificationOTPSerializer(serializers.Serializer):
    """
    Re-sends the signup verification OTP to an unverified (inactive) account.
    """
    email = serializers.EmailField()

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})
        if user.is_active:
            raise serializers.ValidationError({"email": "This account is already verified."})
        return attrs

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        user.generate_otp(test_otp="1234")
        send_mail(
            subject="Verify your account (resend)",
            message=f"Your verification code is {user.otp}. It expires in 10 minutes.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return user




# ===== Login =====
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)



# ===== Password Reset =====
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        user.generate_otp(test_otp="1234")
        send_mail(
            "Password Reset OTP",
            f"Your OTP for password reset is {user.otp}",
            "sakhawatdev5@gmail.com",
            [user.email],
            fail_silently=False,
        )
        return value

class PasswordResetChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_new_password = attrs.get("confirm_new_password")

        if new_password != confirm_new_password:
            raise serializers.ValidationError({"confirm_new_password": "New passwords do not match."})

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["email", "name", "organization", "location", "phone_number"]


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ["facebook", "x", "instagram", "youtube", "truth"]
