from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class PromoConfig(models.Model):
    is_active = models.BooleanField(default=True, verbose_name="Promo Active")
    max_limit = models.IntegerField(default=1000, verbose_name="Promo Limit")

    class Meta:
        verbose_name = "Promo Configuration"
        verbose_name_plural = "Promo Configurations"

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"Promo Config: {'Active' if self.is_active else 'Inactive'} (Limit: {self.max_limit})"


class Subscription(models.Model):
    PACKAGE_CHOICES = [("package-1", "Package 1"), ("package-2", "Package 2")]
    BILLING_CHOICES = [("monthly", "Monthly"), ("yearly", "Yearly")]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    package = models.CharField(max_length=20, choices=PACKAGE_CHOICES)
    billing_interval = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=True)
    is_promo = models.BooleanField(default=False)
    current_period_start = models.DateTimeField(blank=True, null=True)
    current_period_end = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.user.email + " - " + self.package + " (" + self.billing_interval + ")"
    
