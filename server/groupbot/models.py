from django.db import models

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
