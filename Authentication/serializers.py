from rest_framework import serializers
import django.contrib.auth.password_validation as validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from .models import BaseUserProfile, UserProfileReader, UserProfileWriter, SubscriptionTimeStampThrough
from django.contrib.auth.models import User
import Notifications.models as notificationMod
import Comments.models as commentsMod
import Stories.models as storiesMod
# Create your models here.

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', )
        
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token
      
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validators.validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())]  
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

class ReaderSerializer(serializers.ModelSerializer):
    total_stories_viewed = serializers.SerializerMethodField()
    total_stories_liked = serializers.SerializerMethodField()
    total_stories_disliked = serializers.SerializerMethodField()
    
    total_comments_made = serializers.SerializerMethodField()
    total_comments_liked = serializers.SerializerMethodField()
    total_comments_disliked = serializers.SerializerMethodField()
    
    total_subscriptions = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfileReader
        fields = ('id', 
                  'total_stories_viewed', 
                  'total_stories_liked', 
                  'total_stories_disliked',
                  'total_comments_made',
                  'total_comments_liked',
                  'total_comments_disliked',
                  'total_subscriptions')
    
    def get_total_comments_made(self, obj):
        base_user = BaseUserProfile.objects.get(reader = obj)
        return commentsMod.Comment.objects.filter(creator_id = base_user).count()
        
    def get_total_comments_liked(self, obj):
        base_user = BaseUserProfile.objects.get(reader = obj)
        return commentsMod.Comment.objects.filter(likes = base_user).count()
    
    def get_total_comments_disliked(self, obj):
        base_user = BaseUserProfile.objects.get(reader = obj)
        return commentsMod.Comment.objects.filter(dislikes = base_user).count()
    
    def get_total_stories_viewed(self, obj):
        base_user = BaseUserProfile.objects.get(reader = obj)
        return storiesMod.Post.objects.filter(views = base_user).count()
    
    def get_total_stories_liked(self, obj):
        base_user = BaseUserProfile.objects.get(reader = obj)
        return storiesMod.Post.objects.filter(likes = base_user).count()
    
    def get_total_stories_disliked(self, obj):
        base_user = BaseUserProfile.objects.get(reader = obj)
        return storiesMod.Post.objects.filter(dislikes = base_user).count()
    
    def get_total_subscriptions(self, obj):
        return obj.subscribed_to.all().count()
        
class WriterSerializer(serializers.ModelSerializer):
    total_stories_made = serializers.SerializerMethodField()
    total_story_views = serializers.SerializerMethodField()
    total_story_likes = serializers.SerializerMethodField()
    total_story_dislikes = serializers.SerializerMethodField()
    total_subscribers = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfileWriter
        fields = ('__all__')
        
    def get_total_stories_made(self, obj):
        return storiesMod.Post.objects.filter(creator_id = obj).count()
    
    def get_total_story_views(self, obj):
        all_made = storiesMod.Post.objects.filter(creator_id = obj)        
        return sum([post.views.all().count() for post in all_made])
    
    def get_total_story_likes(self, obj):
        all_made = storiesMod.Post.objects.filter(creator_id = obj)        
        return sum([post.likes.all().count() for post in all_made])
    
    def get_total_story_dislikes(self, obj):
        all_made = storiesMod.Post.objects.filter(creator_id = obj)        
        return sum([post.dislikes.all().count() for post in all_made])
    
    def get_total_subscribers(self, obj):
        return UserProfileReader.objects.filter(subscribed_to = obj).count()

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    reader = ReaderSerializer()
    writer = WriterSerializer()
    notifications_num = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = BaseUserProfile
        fields = ('id', 'avatar', 'user','is_premium', 'notifications_num', 'reader', 'writer')
        
    def get_notifications_num(self, obj):
        try:
            mark = notificationMod.MarkedAsRead.objects.get(user = obj)
        except notificationMod.MarkedAsRead.DoesNotExist:
            mark = notificationMod.MarkedAsRead(user = obj)
            mark.save()
        
        total = 0
        
        ao_ids = mark.notifications_ao.values_list('id', flat=True)
        cr_ids = mark.notifications_cr.values_list('id', flat=True)
        sc_ids = mark.notifications_sc.values_list('id', flat=True)
        scom_ids = mark.notifications_scom.values_list('id', flat=True)

        total += notificationMod.AdministrativeOverallNotifications.objects.all().exclude(id__in = ao_ids).count()
        
        if obj.writer:
            total += notificationMod.UserStoryCommentedNotification.objects.filter(receiver = obj.writer).exclude(id__in=scom_ids).count()
        
        subscribed_to = obj.reader.subscribed_to.all()
        if subscribed_to.count() > 0:
            for subscription in subscribed_to:
                subscr_information = SubscriptionTimeStampThrough.objects.get(reader = obj.reader, writer = subscription)
                if subscr_information.receive_notifications:
                    total += notificationMod.UserStoryCreatedNotification.objects.filter(creator = subscription).exclude(created__lt = subscr_information.when_subscribed).exclude(id__in = sc_ids).count()
        
        total += notificationMod.UserCommentRepliedNotification.objects.filter(receiver = obj).exclude(id__in=cr_ids).count()
        
        return total

    def get_avatar(self, obj):
        return obj.avatar.url

class ProfileSerializerForOthers(serializers.ModelSerializer):
    writer = WriterSerializer()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = BaseUserProfile
        fields = ('avatar', 'is_premium', 'writer')

    def get_avatar(self, obj):
        return obj.avatar.url
    
class ProfileSerializerForExtras(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = BaseUserProfile
        fields = ('id', 'is_premium', 'avatar', 'username')
        
    def get_username(self, obj):
        return obj.user.username

    def get_avatar(self, obj):
        return obj.avatar.url