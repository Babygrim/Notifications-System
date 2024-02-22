from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PostGenre(models.Model):
    genre = models.CharField(max_length=20)

    def serializer(self):
        return {
            'id': self.id,
            'genre': self.genre,
        }
        
        
    def __str__(self):
        return self.genre

class Post(models.Model):
    creator_id = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    genre = models.ForeignKey(PostGenre, on_delete=models.DO_NOTHING, null=False)
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
        

    