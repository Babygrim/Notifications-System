from django.db import models
from django.contrib.auth.models import User
from Stories.models import Post
from datetime import datetime

# Create your models here.
class Comment(models.Model):
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_body = models.TextField(null = False)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    
    replies_count = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=datetime.now)            
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)
    
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
                'replies_count': self.replies_count,
                'likes_count':self.likes_count,
                'dislikes_count':self.dislikes_count,
                'comment_body': self.comment_body,
                'created_at': {
                    'date': str(self.date_created).split(' ')[0],
                    'time': (':').join(str(self.date_created).split(' ')[1].split(':')[:2]),
                }
            }, **anotherdict
        }
    
    def serialize_update(self):
        return {
            'replies_count': self.replies_count,
            'likes_count':self.likes_count,
            'dislikes_count':self.dislikes_count,
        }




