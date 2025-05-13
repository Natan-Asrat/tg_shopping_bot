from django.db import models
from account.models import User

# Create your models here.

class GroupPost(models.Model):
    group_id = models.BigIntegerField()
    message_id = models.BigIntegerField()
    text = models.TextField(blank=True, null=True)
    image_links = models.JSONField(default=list)
    media_group_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group_id', 'message_id')

    def __str__(self):
        return f"Post {self.message_id} in group {self.group_id}"

class UserBot(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} (owned by {self.owner})"
