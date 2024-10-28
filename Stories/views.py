from django.shortcuts import render
from .models import *
from django.db.models import Count, Case, When, IntegerField, Sum
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from Authentication.models import BaseUserProfile, SubscriptionTimeStampThrough
import json
from django.db.models import Q, Count, Case, When, IntegerField
from statistics import median
from django.shortcuts import redirect

# Create your views here.
def getAllStories(request):
    if request.method == "GET":
        return render(request, 'stories.html')

def getSingleStory(request, id):
    if request.method == "GET":
        return render(request, "single-story.html", {"context": id})
    
def getStoryPage(request):
    if request.method == "GET":
        req_page = int(request.GET.get('page', 1))
        search_prompt = request.GET.get('search_prompt', None)
        genres = request.GET.get('genres', None)
        tags = request.GET.get('tags', None)
        sort_by = request.GET.get('sort_by', '-likes_count')
        filter_conditions = []
        
        if not sort_by:
            sort_by = 'likes_count'
        
        if genres:
            genres_ids = list(map(int, genres.split(',')))
            genre_condition = Q(genre__id__in = genres_ids)
            filter_conditions.append(genre_condition)

        if tags:
            try:
                tag_ids = list(map(int, tags.split(',')))
                tags_condition = Q(tags__id__in = tag_ids)
                filter_conditions.append(tags_condition)
            except ValueError:
                pass
                

        if search_prompt:
            search_condition = tokenizeSearch(search_prompt)
            
            case_list = [
                Case(
                    When(key, then=search_condition[key]), 
                    default=0, 
                    output_field=IntegerField())
                
                for key in search_condition.keys()
            ]
            
            stories = Post.objects.filter(*filter_conditions).distinct()
            stories = stories.annotate(num_matches=sum(case_list)).order_by('-num_matches')[:100]
            # matches_median = median(stories.values_list('num_matches', flat=True))
            
            # stories = stories.filter(*filter_conditions).order_by(sort_by)[:100]
        else:
            stories = Post.objects.filter(*filter_conditions).order_by(sort_by)[:100]
        
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
        data = json.loads(request.body)
        title = data.get('title', None) # mandatory
        main_text =  data.get('body', None) # mandatory
        genre = data.get('genre', None) # mandatory
        #image = data.get('image', None) # optional
        descr = data.get('description', None) # optional
        tags = data.get('tag_names', None) # optional
        user = BaseUserProfile.objects.get(user = request.user)
        
        if title and main_text and genre:
            create_story = Post(creator_id = user.writer, post_title = title, post_text = main_text, genre=PostGenre.objects.get(pk=int(genre)))
            create_story.save()
            
            if descr:
                create_story.post_description = descr
                create_story.save()
            
            if tags:
                for tag_name in tags.split(','):
                    if len(tag_name) > 0:
                        try:
                            get_tag = PostTags.objects.get(title = tag_name)
                            create_story.tags.add(get_tag)
                        except PostTags.DoesNotExist:
                            get_tag = PostTags(title = tag_name)
                            get_tag.save()
                            create_story.tags.add(get_tag)
                        finally:
                            create_story.save()
                        
        else:
            return JsonResponse({"success": False, "message":"Story missing it's required attribute(s)"})
        
        return JsonResponse({"success": True, "message":"Story created successfully"})
    
def getGenres(request):
    if request.method == "GET":
        genres = PostGenre.objects.annotate(popularity = Count('post')).order_by('popularity')[:25]         #annotate(popularity = Count('post')).order_by('popularity')[:10]
            
        return JsonResponse({"data": [genre.serialize_create_story() for genre in genres]}, safe=False)

def getTags(request):
    if request.method == "GET":
        search = request.GET.get('query', None)

        if search:
            tags = PostTags.objects.filter(title__icontains = search).annotate(popularity = Count('post')).order_by('-popularity')[:5]
            
            return JsonResponse({"success": True, 'tags': [elem.serialize_create_story() for elem in tags]})
        else:
            tags = PostTags.objects.annotate(popularity = Count('post')).order_by('-popularity')[:10]
            
            return JsonResponse({"success": True, 'tags': [elem.serialize_create_story() for elem in tags]})
         
def getWriterStories(request, id):
    if request.method == "GET":
        stories = Post.objects.filter(creator_id__id = id)
        
        return render(request, 'user-stories.html', {'context':[elem.serializer_all() for elem in stories]})
    
def getUserViewHistory(request):
    if request.method == "GET":
        user = request.GET.get('reader')
        
        get_reader = UserProfileReader.objects.get(pk=user)
        get_viewed = UserViewedPosts.objects.get(reader=get_reader)
        
        return JsonResponse({"context": [elem.serializer_all() for elem in get_viewed.posts.all()]})
    
def getDistinctStoryPage(request):
    if request.method == "GET":
        id = int(request.GET.get('story'))
        post = Post.objects.get(pk=id)
        
        check_subscription = False
        check_ownership = False
        #highlight = request.GET.get('comment', None)
        auth = False
        notified = False
        
        if request.user.id:
            auth = True
            sessionData = request.session.get('viewed')
        
            if sessionData == None:
                request.session['viewed'] = {}
                request.session.save()
                
            sessionData = request.session.get('viewed')
            
            user_profile = BaseUserProfile.objects.get(user = request.user)
            check_subscription = post.creator_id in user_profile.reader.subscribed_to.all()
            
            if user_profile.writer:
                check_ownership = post.creator_id == user_profile.writer

            if check_ownership == False:
                get_reader_posts = UserViewedPosts.objects.get(reader=user_profile.reader)

                if post not in get_reader_posts.posts.all():
                    get_reader_posts.posts.add(post)
                    get_reader_posts.save()
                
                else:
                    if id not in sessionData.keys():
                        sessionData.update({id: True})
                        post.creator_id.total_story_views_counter += 1
                        post.views_counter += 1
                        post.save()
                        get_reader_posts.posts.add(post)
                        get_reader_posts.save()
                        request.session.save()

            try:
                notified = SubscriptionTimeStampThrough.objects.get(writer = post.creator_id, reader = user_profile.reader).receive_notifications
            except SubscriptionTimeStampThrough.DoesNotExist:
                notified = False
        
        context = {
            "story": post.serializer_single(),
            "comment_id": int(request.GET.get('comment', -1)),
            "subscribed": check_subscription ,
            "owner": check_ownership,
            "auth": auth,
            "get_notif": notified, 
        }

        return JsonResponse({"data": context})
        
def reactToStory(request):
    if request.method == "POST":
        data = json.loads(request.body)
        story_id = int(data.get('story'))
        story = Post.objects.get(pk=story_id)
        
        if not request.user.is_authenticated:
            return redirect('/')
        
        user = BaseUserProfile.objects.get(id=request.user.id)
        
        if user.writer:
            if user.writer.id == story.creator_id.id:
                return JsonResponse({"success": False, 'reactions': {'likes': story.likes_count, 'dislikes':story.dislikes_count}, 'reason': "You cannot like or dislike your own stories"}) 
        
        sessionData = request.session.get('story_like_variable')
        react_type = data.get('type')
        
        string_story_id = str(story_id)
        
        
        reader_liked_stories = UserLikedPosts.objects.get(reader__id=int(data.get('reader')))
            
        if sessionData == None:
            request.session['story_like_variable'] = {
                    'dislikes': {},
                }
            request.session.save()
            sessionData = request.session.get('story_like_variable')
        
        if react_type == 'like_story':  
            if story in reader_liked_stories.posts.all():
                reader_liked_stories.posts.remove(story)
                story.likes_count -= 1    
            
            else:
                reader_liked_stories.posts.add(story)
                story.likes_count += 1      
                
                if string_story_id in sessionData['dislikes'].keys():
                    story.dislikes_count -= 1

                    sessionData['dislikes'].pop(string_story_id, None)
        
        else:
            if string_story_id in sessionData['dislikes'].keys():
                story.dislikes_count -= 1
                sessionData['dislikes'].pop(string_story_id, None)
            else:
                story.dislikes_count += 1
                sessionData['dislikes'].update({story_id: True})
                
                if story in reader_liked_stories.posts.all():
                    reader_liked_stories.posts.remove(story)
                    story.likes_count -= 1
                    
                    
        request.session.save()
        story.save()
        reader_liked_stories.save()
        #print(sessionData)
        return JsonResponse({"success": True, 'reactions': {'likes': story.likes_count, 'dislikes':story.dislikes_count}})
            
        
def getUserLikedStories(request):
    if request.method == "GET":
        user = request.GET.get('reader')
        
        get_reader = UserProfileReader.objects.get(pk=user)
        get_viewed = UserLikedPosts.objects.get(reader=get_reader)
        
        return JsonResponse({"context": [elem.serializer_all() for elem in get_viewed.posts.all()]})    
    

#########################################
#        ADDITIONAL FUNCTIONS           #
######################################### 

# SEARCH TOKENIZATION
def tokenizeSearch(search_request):
    init = search_request
    tokenized = search_request.split(' ')
    search_query = dict()
    q_query = Q(post_title__icontains = init) | Q(post_description__icontains = init) | Q(creator_id__writer_pseudo__icontains = init) | Q(tags__title__icontains = init)
    search_query[q_query] = len(init)
    
    for word in tokenized:
        q_query = Q(post_title__icontains = word) | Q(post_description__icontains = word) | Q(creator_id__writer_pseudo__icontains = word) | Q(tags__title__icontains = word)
        search_query[q_query] = len(word)
        for j in range(1, len(word)):
            key1 = word[:-j]
            key2 = word[j:]
            q_query = Q(post_title__icontains = key1) | Q(post_description__icontains = key1) | Q(creator_id__writer_pseudo__icontains = key1) | Q(tags__title__icontains = key1) | Q(post_title__icontains = key2) | Q(post_description__icontains = key2) | Q(creator_id__writer_pseudo__icontains = key2) | Q(tags__title__icontains = key2)
            search_query[q_query] = len(key1) + 1
            
            q_query = Q(post_title__icontains = key1) | Q(post_description__icontains = key1) | Q(creator_id__writer_pseudo__icontains = key1) | Q(tags__title__icontains = key1) | Q(post_title__icontains = key2) | Q(post_description__icontains = key2) | Q(creator_id__writer_pseudo__icontains = key2) | Q(tags__title__icontains = key2)
            search_query[q_query] = len(key2)

    return search_query