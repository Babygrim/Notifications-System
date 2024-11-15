from rest_framework import serializers
from .models import Comment
from TestProject.serializers import CustomDateTimeField
from Authentication.serializers import ProfileSerializerForExtras

class CommentSerializer(serializers.ModelSerializer):
    created = CustomDateTimeField()
    creator_id = ProfileSerializerForExtras()
    replies_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    disliked = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'created', 'comment_body', 'likes_count', 'dislikes_count', 'replies_count', 'creator_id', 'story_id', 'parent_comment_id', 'liked', 'disliked')
        
    def get_replies_count(self, obj):
        # This will count all books related to this author
        return Comment.objects.filter(parent_comment_id = obj).count()

    def get_liked(self, obj):
        request = self.context.get('request')
        sessionData = request.session.get('reactions')
        
        return str(obj.id) in sessionData['likes'].keys()
    
    def get_disliked(self, obj):
        request = self.context.get('request')
        sessionData = request.session.get('reactions')

        return str(obj.id) in sessionData['dislikes'].keys()
    
class ReactionCommentSerializer(CommentSerializer):

    class Meta:
        model = Comment
        fields = ('likes_count', 'dislikes_count', 'replies_count')