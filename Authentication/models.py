from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfileWriter(models.Model):
    writer_pseudo = models.CharField(max_length=100, unique=True)
    
    total_likes_counter = models.PositiveBigIntegerField(default=0) 
    total_story_views_counter = models.PositiveBigIntegerField(default=0) 
        
class UserProfileReader(models.Model):
    subscribed_to = models.ManyToManyField(UserProfileWriter, through='SubscriptionTimeStampThrough')

    total_stories_viewed = models.PositiveBigIntegerField(default=0) 
    total_comments_made = models.PositiveBigIntegerField(default=0) 
    total_liked_comments = models.PositiveBigIntegerField(default=0) 
        
    def __str__(self) -> str:
        return super().__str__()
         
class BaseUserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    is_premium = models.BooleanField(default=False)
    
    reader = models.ForeignKey(UserProfileReader, on_delete=models.DO_NOTHING)
    writer = models.ForeignKey(UserProfileWriter, on_delete=models.DO_NOTHING, null=True, blank=True)

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