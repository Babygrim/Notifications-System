from rest_framework import serializers
import django.contrib.auth.password_validation as validators
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from .models import BaseUserProfile, UserProfileReader, UserProfileWriter
from django.contrib.auth.models import User
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
    reader = ReaderSerializer()
    writer = WriterSerializer()
    
    class Meta:
        model = BaseUserProfile
        fields = ('id', 'avatar', 'is_premium', 'reader', 'writer')
        
class ProfileSerializerForOthers(serializers.ModelSerializer):
    writer = WriterSerializer()
    
    class Meta:
        model = BaseUserProfile
        fields = ('avatar', 'is_premium', 'writer')