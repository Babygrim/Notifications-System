from rest_framework import serializers
from TestProject.serializers import CustomDateTimeField
from Authentication.models import BaseUserProfile
from Authentication.serializers import SingelStoryWriterSerializer, AllStoryWriterSerializer
from .models import Post, PostGenre, PostTags

class GenreSerializer(serializers.ModelSerializer):
    popularity = serializers.IntegerField()
    
    class Meta:
        model = PostGenre
        fields = ('__all__')
        
class StoryMetaGenreSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PostGenre
        fields = ('__all__')
        
class TagSerializer(serializers.ModelSerializer):
    popularity = serializers.IntegerField()
    
    class Meta:
        model = PostTags
        fields = ('__all__')

class StoryMetaTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostTags
        fields = ('__all__')
        
class StoriesSerializer(serializers.ModelSerializer):
    creator_id = SingelStoryWriterSerializer()
    created = CustomDateTimeField()
    genre = StoryMetaGenreSerializer()
    tags = StoryMetaTagSerializer(many=True)
    post_image = serializers.SerializerMethodField()
    
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('id',
                  'creator_id',
                  'post_image',
                  'post_title',
                  'post_text',
                  'post_description',
                  'created',
                  'genre',
                  'tags',
                  'post_image',
                  'likes_count',
                  'dislikes_count',
                  'views_count')
        
    def get_post_image(self, obj):
        return obj.post_image.url
    
    def get_likes_count(self, obj):
        return obj.likes.all().count()
    
    def get_dislikes_count(self, obj):
        return obj.dislikes.all().count()
    
    def get_views_count(self, obj):
        return obj.views.all().count()
         
class AllStorySerializer(serializers.ModelSerializer):
    creator_id = AllStoryWriterSerializer()
    created = CustomDateTimeField()
    genre = StoryMetaGenreSerializer()
    tags = StoryMetaTagSerializer(many=True)
    post_image = serializers.SerializerMethodField()
    
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('id',
                  'creator_id', 
                  'created',
                  'post_image',
                  'post_title',
                  'post_description',
                  'likes_count',
                  'dislikes_count',
                  'views_count',
                  'genre',
                  'tags',
                  'liked',
                  'disliked')
        
    def get_post_image(self, obj):
        return obj.post_image.url
    
    def get_likes_count(self, obj):
        return obj.likes.all().count()
    
    def get_dislikes_count(self, obj):
        return obj.dislikes.all().count()
    
    def get_views_count(self, obj):
        return obj.views.all().count()

    # Flags
    def get_liked(self, obj):
        request = self.context.get('request')
        
        if request.user.is_authenticated:
            base_user = BaseUserProfile.objects.get(user = request.user)
            return base_user in obj.likes.all()
        else:
            return False
    
    def get_disliked(self, obj):
        request = self.context.get('request')
        
        if request.user.is_authenticated:
            base_user = BaseUserProfile.objects.get(user = request.user)
            return base_user in obj.dislikes.all()
        else:
            return False