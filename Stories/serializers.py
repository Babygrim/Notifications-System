from rest_framework import serializers
from TestProject.serializers import CustomDateTimeField
from Authentication.serializers import ProfileSerializer
from .models import Post, PostGenre, PostTags
from Authentication.models import BaseUserProfile

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
    creator_id = serializers.SerializerMethodField()
    created = CustomDateTimeField()
    genre = StoryMetaGenreSerializer()
    tags = StoryMetaTagSerializer(many=True)
    post_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('__all__')
        
    def get_creator_id(self, obj):
        return ProfileSerializer(BaseUserProfile.objects.get(writer = obj.creator_id)).data
    
    def get_post_image(self, obj):
        return obj.post_image.url
         
class AllStorySerializer(serializers.ModelSerializer):
    creator_id = serializers.SerializerMethodField()
    created = CustomDateTimeField()
    genre = StoryMetaGenreSerializer()
    tags = StoryMetaTagSerializer(many=True)
    post_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ('id',
                  'creator_id', 
                  'post_image',
                  'post_title',
                  'post_description',
                  'comments_count',
                  'created',
                  'likes_count',
                  'dislikes_count',
                  'views_counter',
                  'genre',
                  'tags')
    
    def get_creator_id(self, obj):
        return ProfileSerializer(BaseUserProfile.objects.get(writer = obj.creator_id)).data
    
    def get_post_image(self, obj):
        return obj.post_image.url