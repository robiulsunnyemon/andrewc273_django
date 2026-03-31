from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CaseSubmission

@receiver(post_save, sender=CaseSubmission)
def update_profile_stats(sender, instance, created, **kwargs):
    if created and instance.user and hasattr(instance.user, 'profile'):
        profile = instance.user.profile
        profile.total_posts += 1
        if instance.press_release:
            # Press release er length character wise count hobe
            profile.total_letters += len(instance.press_release)
        profile.save()