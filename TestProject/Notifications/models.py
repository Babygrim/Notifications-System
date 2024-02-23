from django.db import models
from django.contrib.auth.models import User
from Stories.models import Post
from Comments.models import Comment
import datetime

# Create your models here.
class UserStoryCommentedNotification(models.Model):
    receiver = models.IntegerField(blank=False, null=False)
    source = models.ForeignKey(Post, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    
    def serialize(self):
        if self.creator:
            additional_data = {
                'creator_id': self.creator.id,
                'creator_username': self.creator.username,
            }
        else:
            additional_data = {
                'creator_id': None,
                'creator_username': "Anonymous User"
            }
            
        return {**{
            'id': self.id,
            'post_id': self.source.id,
            'post_title': self.source.post_title,
            'comment_id': self.comment.id,
            'story': True,
            'comment': False,
            'admin': False,
        }, **additional_data}

class UserCommentRepliedNotification(models.Model):
    receiver = models.IntegerField(blank=False, null=False)
    source = models.ForeignKey(Comment, on_delete=models.CASCADE)
    parent_source = models.ForeignKey(Post, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'post_id': self.parent_source.id,
            'post_title': self.parent_source.post_title,
            'comment_id': self.source.id,
            'reply_id': self.source.parent_comment.id if self.source.parent_comment else None,
            'creator_id': self.creator.id if self.creator else None,
            'creator_username': self.creator.username if self.creator else "Anonymous User",
            'story': False,
            'comment': True,
            'admin': False,
        }
        
        
class AdministrativeOverallNotifications(models.Model):
    message_title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    expiration = models.DateField(default=datetime.date.today)
    
    def serialize(self):
        return {
            'id':self.id,
            'message': self.message,
            'expiration_date': self.expiration,
            'story': False,
            'comment': False,
            'admin': True,
        }
        
    def is_created_today(self):
        return self.expiration == datetime.date.today()
    
    def __str__(self) -> str:
        return self.message_title