from django.db import models
from Authentication.models import BaseUserProfile, UserProfileWriter
from django.db.models.signals import post_save
from django.dispatch import receiver
from math import floor
from django.utils import timezone
from Authentication.serializers import ProfileSerializerForExtras
from TestProject.serializers import CustomDateTimeField

# Create your models here.
class UserStoryCommentedNotification(models.Model):
    receiver = models.ForeignKey(UserProfileWriter, on_delete=models.CASCADE)
    source = models.ForeignKey('Stories.Post', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    comment = models.ForeignKey('Comments.Comment', on_delete=models.CASCADE)
    
    def serialize(self):
        return {
            'id': self.id,
            'created': CustomDateTimeField().to_representation(self.created),
            'post_id': self.source.id,
            'post_title': self.source.post_title,
            'comment_id': self.comment.id,
            'comment_creator': ProfileSerializerForExtras(self.comment.creator_id).data,
            'story': False,
            'story_commented': True,
            'comment': False,
            'admin': False,
        }
        
    def whenAdded(self):
        current_datetime = timezone.now()
        object_added_datetime = self.created
        time_difference = current_datetime - object_added_datetime
        minutes = floor(time_difference.total_seconds() / 60)
        hours = floor(minutes / 60)
        days = floor(hours / 24)
        years = floor(days / 365)
        
        return f'{years} years ago' if years > 0 else f'{days} days ago' if days > 0 else f'{hours} hours ago' if hours > 0 else f'{minutes} minutes ago'

class UserCommentRepliedNotification(models.Model):
    receiver = models.ForeignKey(BaseUserProfile, on_delete=models.CASCADE)
    source = models.ForeignKey('Comments.Comment', on_delete=models.CASCADE)
    parent_source = models.ForeignKey('Stories.Post', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    
    def serialize(self):
        return {
            'id': self.id,
            'created': CustomDateTimeField().to_representation(self.created),
            'post_id': self.parent_source.id,
            'post_title': self.parent_source.post_title,
            'reply_id': self.source.id,
            'parent_comment_id': self.source.parent_comment_id.id,
            'creator': ProfileSerializerForExtras(self.source.parent_comment_id.creator_id).data,
            'story': False,
            'story_commented': False,
            'comment': True,
            'admin': False,
        }
        
    def whenAdded(self):
        current_datetime = timezone.now()
        object_added_datetime = self.created
        time_difference = current_datetime - object_added_datetime
        minutes = floor(time_difference.total_seconds() / 60)
        hours = floor(minutes / 60)
        days = floor(hours / 24)
        years = floor(days / 365)
        
        return f'{years} years ago' if years > 0 else f'{days} days ago' if days > 0 else f'{hours} hours ago' if hours > 0 else f'{minutes} minutes ago'
        
        
class AdministrativeOverallNotifications(models.Model):
    message_title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    created = models.DateTimeField(default=timezone.now)
    
    def serialize(self):
        return {
            'id':self.id,
            'message': self.message,
            'created': CustomDateTimeField().to_representation(self.created),
            'story': False,
            'story_commented': False,
            'comment': False,
            'admin': True,
        }

    def whenAdded(self):
        current_datetime = timezone.now()
        object_added_datetime = self.created
        time_difference = current_datetime - object_added_datetime
        minutes = floor(time_difference.total_seconds() / 60)
        hours = floor(minutes / 60)
        days = floor(hours / 24)
        years = floor(days / 365)
        
        return f'{years} years ago' if years > 0 else f'{days} days ago' if days > 0 else f'{hours} hours ago' if hours > 0 else f'{minutes} minutes ago'
    
    def __str__(self) -> str:
        return self.message_title
    
class UserStoryCreatedNotification(models.Model):
    creator = models.ForeignKey(UserProfileWriter, on_delete=models.CASCADE)
    source = models.ForeignKey('Stories.Post', on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    
    def serialize(self):
        return {
            'id':self.id,
            'creator_id': self.creator_id.id,
            'creator_username': self.creator_id.writer_pseudo,
            'created': CustomDateTimeField().to_representation(self.created),
            'postId': self.source.id,
            'post_name': self.source.post_title,
            'story': True,
            'story_commented': False,
            'comment': False,
            'admin': False,
        }
        
    def whenAdded(self):
        current_datetime = timezone.now()
        object_added_datetime = self.created
        time_difference = current_datetime - object_added_datetime
        minutes = floor(time_difference.total_seconds() / 60)
        hours = floor(minutes / 60)
        days = floor(hours / 24)
        years = floor(days / 365)
        
        return f'{years} years ago' if years > 0 else f'{days} days ago' if days > 0 else f'{hours} hours ago' if hours > 0 else f'{minutes} minutes ago'
     
class MarkedAsRead(models.Model):
    user = models.ForeignKey(BaseUserProfile, on_delete=models.CASCADE)
    
    notifications_sc = models.ManyToManyField(UserStoryCreatedNotification)
    notifications_scom = models.ManyToManyField(UserStoryCommentedNotification)
    notifications_cr = models.ManyToManyField(UserCommentRepliedNotification)
    notifications_ao = models.ManyToManyField(AdministrativeOverallNotifications)
    
    
@receiver(post_save, sender=BaseUserProfile)
def markRead(sender, instance, created, **kwargs):
    if created:
        mark = MarkedAsRead(user = instance)
        mark.save()
        