from django.db import models
from Authentication.models import UserProfileReader, UserProfileWriter, BaseUserProfile
from Notifications.models import UserStoryCreatedNotification
from django.db.models.signals import post_save
from django.dispatch import receiver
from Comments.models import Comment
from math import floor
from django.utils import timezone
# Create your models here.

class PostGenre(models.Model):
    genre = models.CharField(max_length=20, unique=True)

    def serializer(self):
        return {
            'id': self.id,
            'genre': self.genre,
        }
        
    def serialize_create_story(self):
        return {
            'id': self.id,
            'genre': self.genre,
            'popularity': self.popularity,
        }
        
    def __str__(self):
        return self.genre

class PostTags(models.Model):
    title = models.CharField(max_length=30, unique=True)
    
    def serializer(self):
        return {
            'id': self.id,
            'tag': self.title,
        }
        
    def serialize_create_story(self):
        return {
            'id': self.id,
            'tag': self.title,
            'popularity': self.popularity,
        }
        
    def __str__(self):
        return self.title
    

class Post(models.Model):
    creator_id = models.ForeignKey(UserProfileWriter, on_delete=models.CASCADE)
    
    post_image = models.ImageField(upload_to ='story_fis/', default='story_fis/default_story.jpeg')
    post_title = models.CharField(max_length = 50, default="No Name")
    post_text = models.TextField(null = False)
    post_description = models.CharField(max_length=100, default="No Description")
    
    comments_count = models.PositiveBigIntegerField(default=0)
    date_created = models.DateTimeField(default=timezone.now)            
    likes_count = models.PositiveBigIntegerField(default=0)
    dislikes_count = models.PositiveBigIntegerField(default=0)
    views_counter = models.PositiveBigIntegerField(default=0)
    
    genre = models.ForeignKey(PostGenre, on_delete=models.DO_NOTHING, null=False)
    tags = models.ManyToManyField(PostTags)
    
    
    def serializer_all(self):
        return {
            "id": self.id,
            "creator": self.creator_id.serialize_load(),
            "title": self.post_title,
            "image": self.post_image.url,
            "description": self.post_description,
            'created_at': self.whenAdded(),
            'genre': self.genre.serializer(),
            'tags': [tag.serializer() for tag in self.tags.all()],
            'views_counter': self.views_counter,
        }
        
    def serializer_all_search_engine(self):
        return {
            "id": self.id,
            "creator": self.creator_id.serialize_load(),
            "title": self.post_title,
            "image": self.post_image.url,
            "description": self.post_description,
            'created_at': self.whenAdded(),
            'genre': self.genre.serializer(),
            'views_counter': self.views_counter,
            'relevancy': self.num_matches,
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
        
    def serializer_single(self):
        return {
            "id": self.id,
            "creator": self.creator_id.serialize_load(),
            "title": self.post_title,
            "body": self.post_text,
            'likes_count': self.likes_count,
            'dislikes_count': self.dislikes_count,
            'comments_count': Comment.objects.filter(post=self, parent_comment=None).count(),
            'created_at': self.whenAdded(),
            'views_counter': self.views_counter,
        }
        
        
class UserLikedPosts(models.Model):
    reader = models.ForeignKey(UserProfileReader, on_delete=models.CASCADE)
    posts = models.ManyToManyField(Post)
    
    def serializer_all(self):
        return {
            "id": self.id,
            "posts": [elem.serializer_all() for elem in self.posts],
        }
        
class UserViewedPosts(models.Model):
    reader = models.ForeignKey(UserProfileReader, on_delete=models.CASCADE)
    posts = models.ManyToManyField(Post)
    
    def serializer_all(self):
        return {
            "id": self.id,
            "posts": [elem.serializer_all() for elem in self.posts],
        }
    

@receiver(post_save, sender=BaseUserProfile)
def user_created(sender, instance, created, **kwargs):
    if created:        
        views = UserViewedPosts(reader = instance.reader)
        views.save()
        
        liked = UserLikedPosts(reader = instance.reader)
        liked.save()
        
        print('Profile Created Successfully')
        
@receiver(post_save, sender=Post)
def story_created(sender, instance, created, **kwargs):
    if created:
        if UserProfileReader.objects.filter(subscribed_to = instance.creator_id).count() > 0:
            notification = UserStoryCreatedNotification(creator=instance.creator_id, source=instance)
            notification.save()
            print("Writer has >0 Subscribers. Notification Created.")
        else:
            print("Writer has 0 Subscribers. Notification Was Not Created")