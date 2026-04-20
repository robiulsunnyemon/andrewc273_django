import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
# clients test payment packages 
PRICE_LOOKUP = {
    ("package-1", "monthly"): "price_1SaZax7Q7Te59nusdChNPWkR",
    ("package-1", "yearly"): "price_1SabM07Q7Te59nus79GBw4cn",
    ("package-2", "monthly"): "price_1TEnlJ7Q7Te59nusQS29qSn6",
    ("package-2", "yearly"): "price_1TEnmG7Q7Te59nus7OhsNnGy",
}

def _get_or_create_customer_id(user):
    # Prefer existing customer tied to this user if we have one.
    try:
        from ..models import Subscription
        sub = Subscription.objects.filter(user=user).first()
        if sub and sub.stripe_customer_id:
            return sub.stripe_customer_id
    except Exception:
        pass

    # Fallback: reuse an existing Stripe customer by email if present.
    try:
        existing = stripe.Customer.list(email=user.email, limit=1)
        if existing.data:
            return existing.data[0].id
    except stripe.StripeError:
        pass

    customer = stripe.Customer.create(email=user.email)
    return customer.id

def create_checkout_session(user, package, billing):
    price_id = PRICE_LOOKUP.get((package, billing))
    if not price_id:
        raise ValueError("Invalid package or billing option.")

    customer_id = _get_or_create_customer_id(user)
    session = stripe.checkout.Session.create(
        customer=customer_id,
        line_items=[{"price": price_id, "quantity": 1}],
        mode="subscription",
        success_url="http://localhost:5173/checkout/success/",
        cancel_url="http://localhost:5173/checkout/failed/",
    )
    return session.url
