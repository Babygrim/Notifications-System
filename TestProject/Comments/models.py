from django.db import models
from Authentication.models import BaseUserProfile
from Notifications.models import UserStoryCommentedNotification
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from math import floor
# Create your models here.
class Comment(models.Model):
    creator = models.ForeignKey(BaseUserProfile, on_delete=models.DO_NOTHING)
    post = models.ForeignKey('Stories.Post', on_delete=models.CASCADE)
    comment_body = models.TextField(null = False)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    
    date_created = models.DateTimeField(default=timezone.now)            
    likes_count = models.PositiveBigIntegerField(default=0)
    dislikes_count = models.PositiveBigIntegerField(default=0)
    
    def serializer(self):
        return { 
                'id': self.id,
                'replies_count': Comment.objects.filter(parent_comment = self).count(),
                'likes_count':self.likes_count,
                'dislikes_count':self.dislikes_count,
                'comment_body': self.comment_body,
                'created_at': self.whenAdded(),
                'creator': self.creator.displayable_name,
                'creator_id': self.creator.id,
            }
    
    def serialize_update(self):
        return {
            'replies_count': Comment.objects.filter(parent_comment = self).count(),
            'likes_count':self.likes_count,
            'dislikes_count':self.dislikes_count,
        }
        
    def whenAdded(self):
        current_datetime = timezone.now()
        object_added_datetime = self.date_created
        time_difference = current_datetime - object_added_datetime
        minutes = floor(time_difference.total_seconds() / 60)
        hours = floor(minutes / 60)
        days = floor(hours / 24)
        years = floor(days / 365)
        
        return f'{years} years ago' if years > 0 else f'{days} days ago' if days > 0 else f'{hours} hours ago' if hours > 0 else f'{minutes} minutes ago'


@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created:
        if instance.parent_comment:
            pass
        else:
            if instance.creator.writer:
                if instance.creator.writer != instance.post.creator_id:
                    notify = UserStoryCommentedNotification(receiver = instance.post.creator_id, source = instance.post, comment = instance)
                    notify.save()
            else:
                notify = UserStoryCommentedNotification(receiver = instance.post.creator_id, source = instance.post, comment = instance)
                notify.save()
            
        print("Notification Created")