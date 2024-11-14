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
    creator_id = WriterSerializer()
    created = CustomDateTimeField()
    genre = StoryMetaGenreSerializer()
    tags = StoryMetaTagSerializer(many=True)
    
    class Meta:
        model = Post
        fields = ('__all__')
        
class AllStorySerializer(serializers.ModelSerializer):
    creator_id = WriterSerializer()
    created = CustomDateTimeField()
    genre = StoryMetaGenreSerializer()
    tags = StoryMetaTagSerializer(many=True)
    
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