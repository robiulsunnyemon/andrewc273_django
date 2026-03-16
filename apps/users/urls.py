from django.urls import path
from .views import (
    SignupView, LoginView,
    PasswordResetRequestAPIView, PasswordResetOTPVerifyView, PasswordResetChangeAPIView, LogoutView, ChangePassword, DeleteAccountAPIView,
    ProfileDetailAPIView, SocialLinkAPIView, VerifyEmailView, ResendVerificationOTPView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Signup
    path("signup/", SignupView.as_view(), name="signup"),

    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),        # Verify OTP and activate
    path("verify-email/resend-otp/", ResendVerificationOTPView.as_view(), name="verify-email-resend-otp"),         # Resend signup OTP

    # Login
    path("login/", LoginView.as_view(), name="login"),

    # Token Refresh
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Password Reset
    path("password-reset/request/", PasswordResetRequestAPIView.as_view(), name="password-reset-request"),
    path("password-reset/verify-otp/", PasswordResetOTPVerifyView.as_view(), name="password-reset-verify-otp"),
    path("password-reset/change-password/", PasswordResetChangeAPIView.as_view(), name="password-reset-change"),

    #change password
    path("change-password/", ChangePassword.as_view(), name="change_password"),

    # Logout
    path("logout/", LogoutView.as_view(), name="logout"),

    # Delete Account
    path('delete-account/', DeleteAccountAPIView.as_view(), name='delete-account'),

    # Profile Details
    path("profile/", ProfileDetailAPIView.as_view(), name="profile-detail"),

    # Social Links
    path("social-links/", SocialLinkAPIView.as_view(), name="social-links"),
]
