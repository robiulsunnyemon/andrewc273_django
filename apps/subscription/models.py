from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Subscription(models.Model):
    PACKAGE_CHOICES = [("package-1", "Package 1"), ("package-2", "Package 2")]
    BILLING_CHOICES = [("monthly", "Monthly"), ("yearly", "Yearly")]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)
    package = models.CharField(max_length=20, choices=PACKAGE_CHOICES)
    billing_interval = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=True)
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.user.email + " - " + self.package + " (" + self.billing_interval + ")"
    
