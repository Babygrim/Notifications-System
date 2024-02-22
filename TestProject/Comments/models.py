from django.db import models
from django.contrib.auth.models import User
from Stories.models import Post


# Create your models here.
class Comment(models.Model):
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_body = models.TextField(null = False)
    #number_of_likes = models.IntegerField()              I don't know if you want to add these
    #number_of_replies.IntegerField()
    
    def serializer(self):
        if self.creator:
            anotherdict = {
            'creator': self.creator.username,
            'creator_id': self.creator.id,
            }
        else:
            anotherdict = {
            'creator': "Anonymous User",
            'creator_id': "Anonymous User",
            }
            
        return { **{
            'id': self.id,
            'comment_body': self.comment_body,
            }, **anotherdict
        }
    
class CommentReply(models.Model):
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    parent_comment_id = models.IntegerField(null=False)             
    comment_body = models.TextField(null = False)
    #number_of_likes = models.IntegerField()              I don't know if you want to add these
    #number_of_replies.IntegerField()

    def serializer(self):
        if self.creator:
            anotherdict = {
            'creator': self.creator.username,
            'creator_id': self.creator.id,
            }
        else:
            anotherdict = {
            'creator': "Anonymous User",
            'creator_id': "Anonymous User",
            }
        return {**{
            'id': self.id,
            'parent_comment_id': self.parent_comment_id,
            'comment_body': self.comment_body,
        }, **anotherdict}




