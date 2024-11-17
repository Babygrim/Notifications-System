from rest_framework import serializers
from TestProject.serializers import CustomDateTimeField
from Authentication.serializers import WriterSerializer
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
    creator_id = serializers.SerializerMethodField()
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
        
    def get_creator_id(self, obj):
        return WriterSerializer(obj.creator_id).data
    
    def get_post_image(self, obj):
        return obj.post_image.url
    
    def get_likes_count(self, obj):
        return obj.likes.all().count()
    
    def get_dislikes_count(self, obj):
        return obj.dislikes.all().count()
    
    def get_views_count(self, obj):
        return obj.views.all().count()
         
class AllStorySerializer(serializers.ModelSerializer):
    creator_id = serializers.SerializerMethodField()
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
                  'post_description',
                  'created',
                  'likes_count',
                  'dislikes_count',
                  'views_count',
                  'genre',
                  'tags')
    
    def get_creator_id(self, obj):
        return WriterSerializer(obj.creator_id).data
    
    def get_post_image(self, obj):
        return obj.post_image.url
    
    def get_likes_count(self, obj):
        return obj.likes.all().count()
    
    def get_dislikes_count(self, obj):
        return obj.dislikes.all().count()
    
    def get_views_count(self, obj):
        return obj.views.all().count()