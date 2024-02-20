from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import *
from Stories.models import Post
from django.http import JsonResponse
from Notifications.models import *

# Create your views here.


def printNoteComment(request, id):
    if request.method == "GET":
        comment = Comment.objects.get(pk=id)
        
        get_replies = CommentReply.objects.filter(parent_comment_id=id)
        context = {
            "comment": comment.serializer(),
            "replies": [elem.serializer() for elem in get_replies],
            "reply_id": int(request.GET.get('reply', -1)),
        }
        return render(request, "comments.html", {"context": context})



def printAllComments(request):
    if request.method == "GET":
        get_all_comments = Comment.objects.all()
        data = [elem.serializer() for elem in get_all_comments]
        return render(request, "comments.html", {"context": data})
    
    elif request.method == "POST":
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
    
    
def ReplyToComment(request, comment_id):
    if request.method == "GET":
        get_all_replies = CommentReply.objects.filter(parent_comment_id = comment_id)
        
        return JsonResponse({"data": [reply.serializer() for reply in get_all_replies]}, safe=True)
    
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
        
        