from rest_framework import serializers
from .models import Comment
from TestProject.serializers import CustomDateTimeField
from Authentication.serializers import ProfileSerializerForComments

class CommentSerializer(serializers.ModelSerializer):
    created = CustomDateTimeField()
    creator_id = ProfileSerializerForComments()
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'created', 'comment_body', 'likes_count', 'dislikes_count', 'replies_count', 'creator_id', 'story_id', 'parent_comment_id')
        
    def get_replies_count(self, obj):
        # This will count all books related to this author
        return Comment.objects.filter(parent_comment_id = obj).count()

class ReactionCommentSerializer(CommentSerializer):

    class Meta:
        model = Comment
        fields = ('likes_count', 'dislikes_count', 'replies_count')