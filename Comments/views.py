from .models import *
from Stories.models import Post
from Notifications.models import *
from django.core.paginator import Paginator
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CommentSerializer

#Fetch comments or replies for comment
class GetComments(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        comment_id = request.GET.get('parent_comment_id', None)
        story_id = request.GET.get('story_id', None)
        req_page = request.GET.get('page', 1)
        
        # meaning get replies else - get main comments
        if comment_id:
            try:
                parent_comment = Comment.objects.get(pk = int(comment_id))
            except Comment.DoesNotExist:
                return Response({"success": False, "data": {}, "message": f'Parent comment with id={comment_id} does not exist'})
            
            get_all_replies = Comment.objects.filter(parent_comment_id = parent_comment).order_by('created')
            paginated = Paginator(get_all_replies, per_page=10)
            get_page = paginated.get_page(req_page)
        
        elif story_id:
            try:
                story = Post.objects.get(pk = int(story_id))
            except Comment.DoesNotExist:
                return Response({"success": False, "data": {}, "message": f'Story with id={story_id} does not exist'})
            
            base_user_by_author = BaseUserProfile.objects.get(writer = story.creator_id)
            
            # make story-author comments appear first
            author_comments = Comment.objects.filter(creator_id = base_user_by_author, story_id = story, parent_comment_id = None).order_by("created")
            get_all_comments = Comment.objects.filter(story_id = story, parent_comment_id = None).exclude(creator_id = base_user_by_author)
            
            # combined
            comments = author_comments | get_all_comments
            
            paginated = Paginator(comments, per_page=20)
            get_page = paginated.get_page(req_page)
        
        else:
            return Response({"success": False, "data": {}, "message": 'parent_comment_id was not passed - no replies fetched, story_id was not passed - no comments fetched'})
        
        response = {
                "page": {
                    "current": get_page.number,
                    "total": paginated.num_pages,
                    "has_next": get_page.has_next(),
                    "has_previous": get_page.has_previous(),
                },
                "data": CommentSerializer(get_page.object_list, many=True, context={'request': request}).data
        }
        return Response({"success": True, "data": response, "message": ''})

#Create comment or reply              
class CreateComments(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def post(self, request):
        # getting the request data
        data = request.data
        
        # fetchin required parameters
        parent_comment_id = data.get('parent_comment_id', None)
        story_id = data.get('story_id', None)
        comment_body = data.get('comment_body', None)
        request_user = BaseUserProfile.objects.get(user = request.user)
        
        if (story_id == None and comment_body == None) or (parent_comment_id == None and comment_body == None):
            return Response({"success": False, "data": {}, "message": f'Request body requires (parent_comment_id, comment_body) or (story_id, comment_body) data combination'})

        # creating replies or nested replies
        if parent_comment_id:
            try:
                get_comment = Comment.objects.get(pk=int(parent_comment_id))
            except Comment.DoesNotExist:
                return Response({"success": False, "data": {}, "message": f'Parent comment with id={parent_comment_id} does not exist'})

            # handle reply creation
            real_parent = get_comment
            while real_parent.parent_comment_id != None:
                real_parent = real_parent.parent_comment_id
            
            story = real_parent.story_id
            if real_parent != get_comment:
                comment_body = f"@{get_comment.creator_id.user.username}, " + comment_body
            
            reply_to_comment = Comment(creator_id = request_user, 
                                       story_id = story, 
                                       parent_comment_id = real_parent, 
                                       comment_body = comment_body)
            
            reply_to_comment.save()
            
            # handle notification creation
            user_to_notify = get_comment.creator_id
            
            if request_user != user_to_notify:
                create_notification = UserCommentRepliedNotification(receiver = user_to_notify, source = reply_to_comment, parent_source = story)
                create_notification.save()
            
            story.save()   
            return Response({"success": True, "data": CommentSerializer(reply_to_comment, context={'request': request}).data, "message": "reply created successfully"})
        
        # creating main comment
        elif story_id:
            try:
                story = Post.objects.get(pk=int(story_id))
            except Post.DoesNotExist:
                return Response({"success": False, "data": {}, "message": f'story with id={story_id} does not exist'})
        
            # handle comment creation
            comment = Comment(creator_id = request_user,
                              story_id = story,
                              comment_body = comment_body)
            
            comment.save()
            
            # handle notification creation
            if request_user != story.creator_id:
                create_notification = UserStoryCommentedNotification(receiver = story.creator_id, source = story, comment = comment)
                create_notification.save()

            story.save()   
            return Response({"success": True, "data": CommentSerializer(comment, context={'request': request}).data, "message": "comment created successfully"})
        

    def delete(self, request):
        comment_id = request.data.get("comment_id", None)
        
        if comment_id == None:
            return Response({"success": False, "data": {}, "message": f"comment_id is not passed in request body"})
        
        try:
            comment = Comment.objects.get(pk = int(comment_id))
        except Comment.DoesNotExist:
            return Response({"success": False, "data": {}, "message": f"comment with specified comment_id={comment_id} does not exist"})
        
        base_user = BaseUserProfile.objects.get(user = request.user)
        
        if comment.story_id.creator_id ==  base_user.writer or comment.creator_id == base_user:
            comment.delete()
            return Response({"success": True, "data": {}, "message": "comment deleted successfully"})
        else:
            return Response({"success": True, "data": {}, "message": "you do not have permission to delete this comment (you must be comment creator or creator of the story that comment is related to)"})
        
#React to comment or reply
class LikeUnlikeComment(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def post(self, request):
        data = request.data
        comment_id = data.get('comment_id', None)
        submission_type = data.get('type', None)
        base_user = BaseUserProfile.objects.get(user = request.user)
    
        if comment_id == None or submission_type == None:
            return Response({"success": False, "data": {}, "message": "request body missing comment_id or type (type should be 'like' or 'dislike')"})
        
        try:
            get_comment = Comment.objects.get(pk = comment_id)
        except Comment.DoesNotExist:
            return Response({"success": False, "data": {}, "message": f"comment with id={comment_id} does not exist."})
            
        if submission_type == 'like':
            if base_user in get_comment.dislikes.all():
                get_comment.dislikes.remove(base_user)
                
            if base_user in get_comment.likes.all():
                get_comment.likes.remove(base_user)
            else:
                get_comment.likes.add(base_user)
        elif submission_type == 'dislike':
            if base_user in get_comment.likes.all():
                get_comment.likes.remove(base_user)
                
            if base_user in get_comment.dislikes.all():
                get_comment.dislikes.remove(base_user)
            else:
                get_comment.dislikes.add(base_user) 
        else:
            return Response({"success": False, "data": {}, "message": "Invalid type (type should be 'like' or 'dislike')"})

        get_comment.save()
        return Response({"success": True, "data": CommentSerializer(get_comment, context={'request': request}).data, "message": ""})
