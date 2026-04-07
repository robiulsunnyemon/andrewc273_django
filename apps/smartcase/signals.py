from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CaseSubmission,CaseDocument
import os



@receiver(post_save, sender=CaseSubmission)
def update_profile_stats(sender, instance, created, **kwargs):
    if created and instance.user and hasattr(instance.user, 'profile'):
        profile = instance.user.profile
        profile.total_posts += 1
        if instance.press_release:
            # Press release er length character wise count hobe
            profile.total_letters += len(instance.press_release)
        profile.save()


@receiver(post_save, sender=CaseDocument)
def check_video_for_star_badge(sender, instance, created, **kwargs):
    if created and instance.file:
        # file check
        ext = os.path.splitext(instance.file.name)[1].lower()
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.mpeg']
        
        if ext in video_extensions:
            # CaseSubmission from user
            user = instance.case.user
            if user and hasattr(user, 'profile'):
                profile = user.profile
                # if profile doesn't have star badge, give it
                if not profile.has_podcast_story:
                    profile.has_podcast_story = True
                    profile.save()