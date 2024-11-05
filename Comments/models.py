from django.db import models
from Authentication.models import BaseUserProfile
from Notifications.models import UserStoryCommentedNotification
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Comment(models.Model):
    creator_id = models.ForeignKey(BaseUserProfile, on_delete=models.DO_NOTHING)
    story_id = models.ForeignKey('Stories.Post', on_delete=models.CASCADE)
    comment_body = models.TextField(null = False)
    parent_comment_id = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    
    created = models.DateTimeField(default=now)            
    likes_count = models.PositiveBigIntegerField(default=0)
    dislikes_count = models.PositiveBigIntegerField(default=0)
         
    def serialize_update(self):
        return {
            'replies_count': Comment.objects.filter(parent_comment = self).count(),
            'likes_count':self.likes_count,
            'dislikes_count':self.dislikes_count,
        }

@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created:
        if instance.parent_comment_id:
            pass
        else:
            if instance.creator_id.writer:
                if instance.creator_id.writer != instance.story_id.creator_id:
                    notify = UserStoryCommentedNotification(receiver = instance.story_id.creator_id, source = instance.story_id, comment = instance)
                    notify.save()
            else:
                notify = UserStoryCommentedNotification(receiver = instance.story_id.creator_id, source = instance.story_id, comment = instance)
                notify.save()
            
        print("Notification Created")