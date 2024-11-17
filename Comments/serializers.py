from rest_framework import serializers
from .models import Comment
from TestProject.serializers import CustomDateTimeField
from Authentication.serializers import ProfileSerializerForExtras
from Authentication.models import BaseUserProfile

class CommentSerializer(serializers.ModelSerializer):
    created = CustomDateTimeField()
    creator_id = ProfileSerializerForExtras()
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()
    creator_is_story_author = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'created', 'comment_body', 'likes_count', 'dislikes_count', 'replies_count', 'creator_id', 'story_id', 'parent_comment_id', 'liked', 'disliked', 'creator_is_story_author')
    
    # counters
    def get_replies_count(self, obj):
        return Comment.objects.filter(parent_comment_id = obj).count()

    def get_likes_count(self, obj):
        return obj.likes.all().count()    
    
    def get_dislikes_count(self, obj):
        return obj.dislikes.all().count()
    
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
        
    def get_creator_is_story_author(self, obj):
        return obj.creator_id.writer == obj.story_id.creator_id