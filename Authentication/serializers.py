from rest_framework import serializers
import django.contrib.auth.password_validation as validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from .models import BaseUserProfile, UserProfileReader, UserProfileWriter, SubscriptionTimeStampThrough
from django.contrib.auth.models import User
from Notifications.models import *
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
    class Meta:
        model = UserProfileReader
        fields = ('__all__')
        
class WriterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileWriter
        fields = ('__all__')

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    reader = ReaderSerializer()
    writer = WriterSerializer()
    notifications_num = serializers.SerializerMethodField()
    
    class Meta:
        model = BaseUserProfile
        fields = ('id', 'avatar', 'user','is_premium', 'notifications_num', 'reader', 'writer')
        
    def get_notifications_num(self, obj):
        try:
            mark = MarkedAsRead.objects.get(user = obj)
        except MarkedAsRead.DoesNotExist:
            mark = MarkedAsRead(user = obj)
            mark.save()
        
        total = 0
        
        ao_ids = mark.notifications_ao.values_list('id', flat=True)
        cr_ids = mark.notifications_cr.values_list('id', flat=True)
        sc_ids = mark.notifications_sc.values_list('id', flat=True)
        scom_ids = mark.notifications_scom.values_list('id', flat=True)

        total += AdministrativeOverallNotifications.objects.all().exclude(id__in = ao_ids).count()
        
        if obj.writer:
            total += UserStoryCommentedNotification.objects.filter(receiver = obj.writer).exclude(id__in=scom_ids).count()
        
        subscribed_to = obj.reader.subscribed_to.all()
        if subscribed_to.count() > 0:
            for subscription in subscribed_to:
                subscr_information = SubscriptionTimeStampThrough.objects.get(reader = obj.reader, writer = subscription)
                if subscr_information.receive_notifications:
                    total += UserStoryCreatedNotification.objects.filter(creator = subscription).exclude(created__lt = subscr_information.when_subscribed).exclude(id__in = sc_ids).count()
        
        total += UserCommentRepliedNotification.objects.filter(receiver = obj).exclude(id__in=cr_ids).count()
        
        return total
        
        
class ProfileSerializerForOthers(serializers.ModelSerializer):
    writer = WriterSerializer()
    
    class Meta:
        model = BaseUserProfile
        fields = ('avatar', 'is_premium', 'writer')

class ProfileSerializerForExtras(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    
    class Meta:
        model = BaseUserProfile
        fields = ('id', 'is_premium', 'avatar', 'username')
        
    def get_username(self, obj):
        return obj.user.username