from django.shortcuts import render
from .models import *
from django.http import HttpResponseRedirect
from Comments.models import Comment


# Create your views here.
def getAllStories(request):
    if request.method == "GET":
        return render(request, "stories.html", {"context":[elem.serializer_all() for elem in Post.objects.all()]})
    
    elif request.method == "POST":
        data = request.POST
        create_story = Post(creator_id = request.user, post_title = data.get('title', "Story Title Lost"), post_text = data.get('body', 'Story Text Lost'))
        create_story.save()
        
        return HttpResponseRedirect(data.get('next', '/'))

def getSingleStory(request, id):
    post = Post.objects.get(pk=id)
    story_comments = Comment.objects.filter(post=post)
    
    context = {
        "story": post.serializer_single(),
        "comments": [elem.serializer() for elem in story_comments],
        "comment_id": int(request.GET.get('comment', -1)),
    }
    
    return render(request, "single-story.html", {"context": context})
    