from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.subscription.models import Subscription, PromoConfig

User = get_user_model()

class PromoSubscriptionTests(APITestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(email="testuser1@example.com", password="password123")
        self.user2 = User.objects.create_user(email="testuser2@example.com", password="password123")
        
        # Reset promo config to active with limit 2
        self.promo_config = PromoConfig.get_solo()
        self.promo_config.is_active = True
        self.promo_config.max_limit = 2
        self.promo_config.save()

    def test_promo_status_anonymous(self):
        response = self.client.get("/api/v1/subscription/promo-status/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertTrue(response.data["data"]["is_active"])
        self.assertEqual(response.data["data"]["max_limit"], 2)
        self.assertEqual(response.data["data"]["current_count"], 0)
        self.assertTrue(response.data["data"]["is_eligible"])

    def test_claim_promo_success(self):
        # Login user1
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.post("/api/v1/subscription/claim-promo/")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        
        # Check subscription details in DB
        sub = Subscription.objects.get(user=self.user1)
        self.assertEqual(sub.package, "package-1")
        self.assertEqual(sub.billing_interval, "lifetime")
        self.assertTrue(sub.is_active)
        self.assertTrue(sub.is_promo)
        self.assertIsNone(sub.current_period_end)

    def test_claim_promo_already_subscribed(self):
        # Create user1 subscription first
        Subscription.objects.create(
            user=self.user1,
            package="package-2",
            billing_interval="monthly",
            is_active=True
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post("/api/v1/subscription/claim-promo/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_claim_promo_inactive_promo(self):
        # Set promo to inactive
        self.promo_config.is_active = False
        self.promo_config.save()
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post("/api/v1/subscription/claim-promo/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_claim_promo_limit_reached(self):
        # Fill the limit (limit is 2)
        # Create 2 promo subscriptions
        Subscription.objects.create(
            user=self.user1,
            package="package-1",
            billing_interval="lifetime",
            is_promo=True,
            is_active=True
        )
        user_dummy = User.objects.create_user(email="dummy@example.com", password="password123")
        Subscription.objects.create(
            user=user_dummy,
            package="package-1",
            billing_interval="lifetime",
            is_promo=True,
            is_active=True
        )
        
        # Now try to claim with user2
        self.client.force_authenticate(user=self.user2)
        response = self.client.post("/api/v1/subscription/claim-promo/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("limit has been reached", response.data["message"])
