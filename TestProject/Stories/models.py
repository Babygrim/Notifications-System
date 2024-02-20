from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    creator_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    post_title = models.CharField(max_length = 50, default="No Name")
    post_text = models.TextField(null = False)
    
    def serializer_all(self):
        return {
            "id": self.id,
            "creator_id": self.creator_id.id,
            "creator_username": self.creator_id.username,
            "title": self.post_title,
        }
        
    def serializer_single(self):
        return {
            "id": self.id,
            "creator_id": self.creator_id.id,
            "creator_username": self.creator_id.username,
            "title": self.post_title,
            "body": self.post_text,
        }