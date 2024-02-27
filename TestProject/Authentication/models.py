from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from .serializers import UserSerializer

def generateNumbers():
    return ('').join([str(num) for num in random.choices([i for i in range(10)], k=8)])

class UserProfileWriter(models.Model):
    writer_pseudo = models.CharField(max_length=100, default=f'User-{generateNumbers()} Author')
    
    subscribers_counter = models.PositiveBigIntegerField(default=0) 
    total_likes_counter = models.PositiveBigIntegerField(default=0) 
    total_story_views_counter = models.PositiveBigIntegerField(default=0) 
    
    def serialize_load(self):
        return {
            'id': self.id,
            'writer_pseudo': self.writer_pseudo,
            'subscribers_counter': self.subscribers_counter, 
            'total_likes_counter': self.total_likes_counter, 
            'total_story_views_counter': self.total_story_views_counter,
        }
        
class UserProfileReader(models.Model):
    subscribed_to = models.ManyToManyField(UserProfileWriter, through='SubscriptionTimeStampThrough')

    total_stories_viewed = models.PositiveBigIntegerField(default=0) 
    total_comments_made = models.PositiveBigIntegerField(default=0) 
    total_liked_comments = models.PositiveBigIntegerField(default=0) 

    def serialize_load(self):
        return {
            'reader_id': self.id,
        }
    
    def serialize_info(self):
        return {
            'id': self.id,
            'total_stories_viewed': self.total_stories_viewed, 
            'total_comments_made': self.total_comments_made, 
            'total_liked_comments': self.total_liked_comments, 
        }
        
    def serialize_subscription(self):
        return {
            'id': self.id,
            'subscribed_to': self.subscribed_to,
        }
        
    def __str__(self) -> str:
        return super().__str__()
         
class BaseUserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    displayable_name = models.CharField(max_length=20, default=f'User-{generateNumbers()}')
    is_premium = models.BooleanField(default=False)
    
    reader = models.ForeignKey(UserProfileReader, on_delete=models.DO_NOTHING)
    writer = models.ForeignKey(UserProfileWriter, on_delete=models.DO_NOTHING, null=True, blank=True)
    
    def serialize(self):
        return {
            'id': self.id,
            'bound_user': UserSerializer(self.user).data,
            'avatar': self.avatar.url,
            'displayable_name': self.displayable_name,
            'premium': self.is_premium,
            'bound_reader_profile': self.reader.serialize_load() if self.reader else None,
            'bound_writer_profile': self.writer.serialize_load() if self.writer else None,
        }
        
    def serialize_notif(self):
        return {
            'user_id': self.id,
            'name': self.displayable_name,
        }

class SubscriptionTimeStampThrough(models.Model):
    writer = models.ForeignKey(UserProfileWriter, on_delete = models.CASCADE)
    reader = models.ForeignKey(UserProfileReader, on_delete = models.CASCADE)
    when_subscribed = models.DateTimeField(default=timezone.now)
    receive_notifications = models.BooleanField(default=True)


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        reader = UserProfileReader()
        reader.save()
        
        profile = BaseUserProfile(user=instance, reader = reader)
        profile.save()        
        print('Profile Created Successfully')