from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import *
from Stories.models import Post
from django.http import JsonResponse
from Notifications.models import *
from django.core.paginator import Paginator
import json

# Create your views here.
  
def getCommentReplies(request):
    if request.method == "GET":
        comment_id = request.GET.get('parent')
        req_page = request.GET.get('page', 1)
        
        get_all_replies = Comment.objects.filter(parent_comment__id = comment_id).order_by('-date_created')
        
        paginated = Paginator(get_all_replies, per_page=10)

        get_page = paginated.get_page(req_page)
    
        payload = [elem.serializer() for elem in get_page.object_list]

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
            reply_to_comment = Comment(creator = request.user, post = story, parent_comment = get_comment, comment_body = data.get('comment_body', 'Reply Text Got Lost'))
            reply_to_comment.save()
            
            if get_comment.creator:
                notification = UserCommentRepliedNotification(receiver = get_comment.creator.id, source=get_comment, parent_source = story, creator = request.user)
                notification.save()
        else:
            reply_to_comment = Comment(parent_comment = get_comment, comment_body = data.get('comment_body', 'Reply Text Got Lost'))
            reply_to_comment.save()
            
            if get_comment.creator:
                notification = UserCommentRepliedNotification(receiver = get_comment.creator.id, source=get_comment, parent_source = story)
                notification.save()
        
        get_comment.replies_count += 1
        get_comment.save()
        return HttpResponseRedirect(data.get('next', '/'))
        
def getStoryComments(request):
    if request.method == "GET":
        story_id = request.GET.get('story_id')
        req_page = request.GET.get('page', 1)
        
        get_comments = Comment.objects.filter(post=Post.objects.get(pk=story_id), parent_comment = None).order_by('-date_created')
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

def LikeUnlikeComment(request):
    if request.method == "POST":
        data = json.loads(request.body)
        comment_id = int(data.get('comment_id'))
        sessionData = request.session.get('reactions')
        submission_type = data.get('type')
        get_comment = Comment.objects.get(pk = comment_id)
        
        if sessionData == None:
            request.session['reactions'] = {
                    'likes': {},
                    'dislikes': {},
                }
            request.session.save()
            sessionData = request.session.get('reactions')
        
        # work with sessionData variable
        check_comment_liked = True if str(comment_id) in sessionData['likes'].keys() else False
        check_comment_disliked = True if str(comment_id) in sessionData['dislikes'].keys() else False
        
        if submission_type == 'like':
            if check_comment_liked:
                get_comment.likes_count -= 1
                get_comment.save()
                sessionData['likes'].pop(str(comment_id), None)
            else:
                get_comment.likes_count += 1
                get_comment.save()
                sessionData['likes'].update({comment_id: True})
                
                if check_comment_disliked:
                    get_comment.dislikes_count -= 1
                    get_comment.save()
                    sessionData['dislikes'].pop(str(comment_id), None)
                            
        elif submission_type == 'dislike':
            if check_comment_disliked:
                get_comment.dislikes_count -= 1
                get_comment.save()
                sessionData['dislikes'].pop(str(comment_id), None)
            else:
                get_comment.dislikes_count += 1
                get_comment.save()
                sessionData['dislikes'].update({comment_id: True})
                
                if check_comment_liked:
                    get_comment.likes_count -= 1
                    get_comment.save()
                    sessionData['likes'].pop(str(comment_id), None)
                
        request.session['reactions'] = sessionData
        request.session.save()

        return JsonResponse({"data": get_comment.serialize_update()}, safe=False)