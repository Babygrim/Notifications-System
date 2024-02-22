from django.shortcuts import render
from .models import *
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.core.paginator import Paginator


# Create your views here.
def getAllStories(request):
    if request.method == "GET":
        return render(request, 'stories.html')

def getSingleStory(request, id):
    post = Post.objects.get(pk=id)
    context = {
        "story": post.serializer_single(),
        "comment_id": int(request.GET.get('comment', -1)),
    }
    
    return render(request, "single-story.html", {"context": context})
    
def getStoryPage(request):
    req_page = int(request.GET.get('page', 1))
    
    stories = Post.objects.all().order_by('post_title')
    
    paginated_stories = Paginator(stories, per_page=10)
    get_page = paginated_stories.get_page(req_page)
    
    payload = [elem.serializer_all() for elem in get_page.object_list]

    response = {
            "page": {
                "current": get_page.number,
                "has_next": get_page.has_next(),
                "has_previous": get_page.has_previous(),
                "overall": paginated_stories.num_pages,
            },
            "stories": payload,
    }
    
    return JsonResponse({"data": response})

def createStory(request):
    if request.method == "GET":
        return render(request, 'create-story.html')
    
    elif request.method == "POST":
        data = request.POST
        genres = data.get('genre')
        
        
        create_story = Post(creator_id = request.user, post_title = data.get('title', "Story Title Lost"), post_text = data.get('body', 'Story Text Lost'), genre=PostGenre.objects.get(pk=int(genres)))
        create_story.save()
        
        return HttpResponseRedirect(data.get('next', '/'))
    
def getGenres(request):
    if request.method == "GET":
        genres = PostGenre.objects.all()     
        return JsonResponse({"data": [genre.serializer() for genre in genres]}, safe=False)