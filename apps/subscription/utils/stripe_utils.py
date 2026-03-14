import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
# clients test payment packages 
PRICE_LOOKUP = {
    ("package-1", "monthly"): "price_1SaZax7Q7Te59nusdChNPWkR",
    ("package-1", "yearly"): "price_1SabM07Q7Te59nus79GBw4cn",
}

def create_checkout_session(user, package, billing):
    price_id = PRICE_LOOKUP[(package, billing)]
    customer = stripe.Customer.create(email=user.email)
    session = stripe.checkout.Session.create(
        customer=customer.id,
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        subscription_data={
            "trial_period_days": 14,   # Added 14-day free trial here
        },
        success_url=f"https://booknlink.com/success-checkout/",
        cancel_url=f"https://booknlink.com/failed-checkout/",
    )
    return session.url
