from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    SignupSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetChangeSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    SocialLinkSerializer,
    EmailVerificationSerializer,
    ResendVerificationOTPSerializer
)
from .models import Profile, SocialLink
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework import generics

User = get_user_model()

# ===== Helper Function =====
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class BaseAPIView(APIView):
    def success_response(self, message="Your request Accepted", data=None, status_code=status.HTTP_200_OK):
        return Response(
            {"success": True, "message": message, "status": status_code, "data": data or {}},
            status=status_code
        )

    def error_response(self, message="Your request rejected", data=None, status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {"success": False, "message": message, "status": status_code, "data": data or {}},
            status=status_code
        )



class SignupView(BaseAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            # user.generate_otp()
            # user.save()
           
            user.generate_otp()
            

            # user.save()
            send_mail(
                subject="Verify your account",
                message=f"Your verification code is {user.otp}. It expires in 10 minutes.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            profile = getattr(user, 'profile', None)
            return self.success_response(
                "User created successfully. Please verify your email.",
                data={
                    "email": user.email,
                }
            )
        return self.error_response("Validation error", data=serializer.errors)





class VerifyEmailView(BaseAPIView):
    """
    POST /auth/verify-email/
    Activates account after verifying the OTP sent during signup.
    """
    permission_classes = []

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return self.success_response("Email verified successfully. You can now log in.")
        return self.error_response("Verification failed.", data=serializer.errors)


class ResendVerificationOTPView(BaseAPIView):
    """
    POST /auth/verify-email/resend-otp/
    Re-sends the signup verification OTP for inactive accounts.
    """
    permission_classes = []

    def post(self, request):
        serializer = ResendVerificationOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.success_response("Verification code sent again to your email.")
        return self.error_response("Could not resend verification code.", data=serializer.errors)






# ===== Login =====
class LoginView(BaseAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user_obj = User.objects.filter(email=email).first()
            if user_obj and not user_obj.is_active:
                return self.error_response("Email not verified", status_code=status.HTTP_403_FORBIDDEN)
            user = authenticate(request, email=email, password=password)
            if user is None:
                return self.error_response("Invalid email or password", status_code=status.HTTP_401_UNAUTHORIZED)
            
            tokens = get_tokens_for_user(user)
            return self.success_response("Login successful", data={"tokens": tokens, "user": {"id": user.id,"email": user.email, "is_staff": user.is_staff}} )
        return self.error_response("Invalid data", status_code=status.HTTP_400_BAD_REQUEST)





# ===== Password Reset =====
class PasswordResetRequestAPIView(BaseAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            return self.success_response("OTP sent to email.", data={"email": serializer.validated_data["email"]})
        return self.error_response("Validation error", data=serializer.errors)


class PasswordResetOTPVerifyView(BaseAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        otp = request.data.get("otp")
        if not otp:
            return self.error_response("OTP is required.")

        try:
            user = User.objects.get(otp=otp, otp_exp__gte=timezone.now(), otp_verified=False)
        except User.DoesNotExist:
            return self.error_response("Invalid or expired OTP.")

        user.otp_verified = True
        user.save()
        tokens = get_tokens_for_user(user)  # Access + Refresh token
        return self.success_response(
            "OTP verified successfully.",
            data={"tokens": tokens}
        )

class PasswordResetChangeAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordResetChangeSerializer(data=request.data)
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data["new_password"])
            request.user.otp_verified = False
            request.user.otp = None
            request.user.otp_exp = None
            request.user.save()
            return self.success_response("Password reset successful.")
        return self.error_response("Passwords do not match.", data=serializer.errors)



# ===== Password Change =====
class ChangePassword(BaseAPIView, generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return self.error_response("Validation error", data=serializer.errors)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return self.error_response("Old password does not match")

        user.set_password(new_password)
        user.save()
        return self.success_response("Password changed successfully")



# ===== Logout =====
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": f"Logout failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        



class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete() # For Permanent Delete
        # user.is_active = False  # For Soft delete
        # user.email = f"deleted_{user.id}_{user.email}" # For Soft delete
        # user.save() # For Soft delete
        return Response({"message": "Your account has been deleted."}, status=status.HTTP_200_OK)


# ===== Profile Details =====
class ProfileDetailAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return self.success_response("Profile fetched successfully.", data=serializer.data)

    def put(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response("Profile updated successfully.", data=serializer.data)
        return self.error_response("Validation error", data=serializer.errors)


# ===== Social Links =====
class SocialLinkAPIView(BaseAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        social_link, _ = SocialLink.objects.get_or_create(user=request.user)
        serializer = SocialLinkSerializer(social_link)
        return self.success_response("Social links fetched successfully.", data=serializer.data)

    def put(self, request):
        social_link, _ = SocialLink.objects.get_or_create(user=request.user)
        serializer = SocialLinkSerializer(social_link, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.success_response("Social links updated successfully.", data=serializer.data)
        return self.error_response("Validation error", data=serializer.errors)






from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from urllib.parse import urlparse
import io
from PIL import Image
import requests
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.base import ContentFile





class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        try:
            # let allauth handle authentication
            response = super().post(request, *args, **kwargs)

            user = getattr(self, "user", None) or request.user

            if not user or not user.is_authenticated:
                return Response(
                    {"error": "Authentication failed."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure profile exists
            profile, created = Profile.objects.get_or_create(user=user)
            SocialLink.objects.get_or_create(user=user)

            # Google data
            social_account = user.socialaccount_set.first()
            extra_data = social_account.extra_data if social_account else {}

            first_name = extra_data.get("given_name", "") or ""
            last_name = extra_data.get("family_name", "") or ""
            picture_url = extra_data.get("picture", None)

            # ---------------------------
            # Update Profile fields
            # ---------------------------
            if first_name:
                profile.first_name = first_name

            if last_name:
                profile.last_name = last_name

            full_name = " ".join([first_name, last_name]).strip()
            if full_name:
                profile.name = full_name
            else:
                # fallback
                if not profile.name:
                    profile.name = user.email.split("@")[0]

            # ---------------------------
            # Download and save avatar
            # ---------------------------
            if picture_url and not profile.avatar:
                try:
                    r = requests.get(picture_url, timeout=10)
                    if r.status_code == 200 and r.content:
                        try:
                            img = Image.open(io.BytesIO(r.content))
                            img_type = img.format.lower()
                        except Exception:
                            img_type = None

                        if img_type in ("jpeg", "png", "gif", "bmp", "webp"):
                            filename = urlparse(picture_url).path.split("/")[-1]

                            if not filename:
                                filename = f"user_{user.id}_google.{img_type}"

                            if not filename.lower().endswith(
                                (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")
                            ):
                                ext = "jpg" if img_type == "jpeg" else img_type
                                filename = f"{filename}.{ext}"

                            profile.avatar.save(
                                filename,
                                ContentFile(r.content),
                                save=False
                            )
                except Exception:
                    pass

            profile.save()

            # keep user active
            user.is_active = True
            user.save()

            # JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response(
                {
                    "success": True,
                    "message": "Google login successful.",
                    "status": status.HTTP_200_OK,
                    "data": {
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                        "user": {
                            "id": user.id,
                            "email": user.email,
                            "is_staff": user.is_staff,
                            "first_name": profile.first_name,
                            "last_name": profile.last_name,
                            "name": profile.name,
                            "avatar": (
                                request.build_absolute_uri(profile.avatar.url)
                                if profile.avatar else None
                            ),
                        },
                    }
                },
                status=status.HTTP_200_OK
            )

        except OAuth2Error as e:
            return Response(
                {
                    "error": "Failed to fetch Google user info.",
                    "detail": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as exc:
            return Response(
                {
                    "error": "Google login failed.",
                    "detail": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )