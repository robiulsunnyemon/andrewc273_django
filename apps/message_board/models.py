from django.db import models
from django.contrib.auth import get_user_model
from apps.resources.models import Prison

User = get_user_model()

class Post(models.Model):
    CATEGORY_CHOICES = (
        ('announcements', 'Announcements'),
        ('reform', 'Prison Reform'),
        ('legal', 'Legal Updates'),
        ('support', 'Family Support'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_board_posts')
    title = models.CharField(max_length=255)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='support')
    prison = models.ForeignKey(Prison, on_delete=models.SET_NULL, related_name='message_board_posts', null=True, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.title} by {self.user.email}"


class PostAttachment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_board/attachments/')
    file_type = models.CharField(max_length=50) # e.g. 'image', 'video', 'pdf', 'document'
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment {self.id} for post {self.post.id}"


class PostReaction(models.Model):
    REACTION_CHOICES = (
        ('like', 'Like'),
        ('helpful', 'Helpful'),
        ('warning', 'Warning'),
        ('watching', 'Watching'),
        ('important', 'Important'),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_board_reactions')
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.email} reacted {self.reaction_type} to post {self.post.id}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_board_comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='replies', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.email} on post {self.post.id}"


class PostReport(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_board_reports')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"Report by {self.user.email} on post {self.post.id}"
