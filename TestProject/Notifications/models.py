from django.db import models
from django.contrib.auth.models import User
from Stories.models import Post
from Comments.models import Comment, CommentReply


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
        }, **additional_data}

class UserCommentRepliedNotification(models.Model):
    receiver = models.IntegerField(blank=False, null=False)
    source = models.ForeignKey(Comment, on_delete=models.CASCADE)
    parent_source = models.ForeignKey(Post, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    reply_comment = models.ForeignKey(CommentReply, on_delete=models.CASCADE)
    
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
            'post_id': self.parent_source.id,
            'post_title': self.parent_source.post_title,
            'comment_id': self.source.id,
            'reply_id': self.reply_comment.id,
        }, **additional_data}