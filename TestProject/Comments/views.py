from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import *
from Stories.models import Post
from django.http import JsonResponse
from Notifications.models import *
from django.core.paginator import Paginator

# Create your views here.
  
def getCommentReplies(request):
    if request.method == "GET":
        comment_id = request.GET.get('parent')
        req_page = request.GET.get('page', 1)
        
        get_all_replies = CommentReply.objects.filter(parent_comment_id = comment_id)
        
        paginated = Paginator(get_all_replies, per_page=4)

        get_page = paginated.get_page(req_page)
    
        payload = [elem.serializer_all() for elem in get_page.object_list]

        response = {
                "page": {
                    "current": get_page.number,
                    "has_next": get_page.has_next(),
                    "has_previous": get_page.has_previous(),
                },
                "replies": payload
        }
        return JsonResponse({"data": response}, safe=True)
    
    elif request.method == "POST":
        data = request.POST

        story = Post.objects.get(pk=data.get('post_id'))
        get_comment = Comment.objects.get(pk=data.get('parent_id'))
        
        
        if request.user.id:
            reply_to_comment = CommentReply(creator = request.user, parent_comment_id = data.get('parent_id'), comment_body = data.get('comment_body', 'Reply Text Got Lost'))
            reply_to_comment.save()
            if get_comment.creator:
                notification = UserCommentRepliedNotification(receiver = get_comment.creator.id, source=get_comment, parent_source = story, creator = request.user, reply_comment=reply_to_comment)
                notification.save()
        else:
            reply_to_comment = CommentReply(parent_comment_id = data.get('parent_id'), comment_body = data.get('comment_body', 'Reply Text Got Lost'))
            reply_to_comment.save()
            if get_comment.creator:
                notification = UserCommentRepliedNotification(receiver = get_comment.creator.id, source=get_comment, parent_source = story, reply_comment=reply_to_comment)
                notification.save()
        
        return HttpResponseRedirect(data.get('next', '/'))
        
def getStoryComments(request):
    if request.method == "GET":
        story_id = request.GET.get('story_id')
        req_page = request.GET.get('page', 1)
        
        get_comments = Comment.objects.filter(post=Post.objects.get(pk=story_id))
        paginated_comments = Paginator(get_comments, per_page=10)
        get_page = paginated_comments.get_page(req_page)
        
        payload = [elem.serializer() for elem in get_page.object_list]
        
        response = {
            "page": {
                "current": get_page.number,
                "has_next": get_page.has_next(),
                "has_previous": get_page.has_previous(),
                "overall": paginated_comments.num_pages,
            },
            "stories": payload,
        }
        
        return JsonResponse({"data": response})
    
    if request.method == "POST":
        data = request.POST
        story = Post.objects.get(pk=data.get('post_id'))
        
        
        if request.user.id:
        
            create_comment = Comment(creator = request.user, post = story, comment_body = data.get('comment_body', 'Comment Body Lost'))
            create_comment.save()
            notification = UserStoryCommentedNotification(receiver= story.creator_id.id, source = story, creator = request.user, comment=create_comment)
            notification.save()
            
        else:
            
            create_comment = Comment(post = story, comment_body = data.get('comment_body', 'Comment Body Lost'))
            create_comment.save()
       
        
        return HttpResponseRedirect(data.get('next', '/'))
