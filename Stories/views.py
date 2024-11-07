from django.shortcuts import render
from .models import *
from django.db.models import Count, Case, When, IntegerField
from django.http import JsonResponse
from django.core.paginator import Paginator
from Authentication.models import BaseUserProfile, SubscriptionTimeStampThrough
import json
from django.db.models import Q, Count, Case, When, IntegerField
from statistics import median
from django.shortcuts import redirect
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import StoriesSerializer, GenreSerializer, TagSerializer
from .permissions import IsAuthenticatedWriter

#Fetch all stories there is (plus search)
class GetAllStories(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        req_page = int(request.GET.get('page', 1))
        search_prompt = request.GET.get('search_prompt', None)
        genres = request.GET.get('genres', None)
        tags = request.GET.get('tag', None)
        sort_by = request.GET.get('sort_by', None)
        filter_conditions = []
        
        if not sort_by:
            sort_by = 'likes_count'
        
        if genres:
            genres_ids = list(map(int, genres.split(',')))
            genre_condition = Q(genre__id__in = genres_ids)
            filter_conditions.append(genre_condition)

        if tags:
            genres_ids = list(map(int, tags.split(',')))
            tag_condition = Q(tags__id__in = genres_ids)
            filter_conditions.append(tag_condition)

        if search_prompt:
            search_condition = tokenizeSearch(search_prompt)
            
            case_list = []
            for key in search_condition.keys():
                case_list.append(
                    Case(
                        When(key, then=search_condition[key]), 
                        default=0, 
                        output_field=IntegerField())
                )
            stories = Post.objects.annotate(num_matches=sum(case_list)).order_by('-num_matches')[:100]
            # matches_median = median(stories.values_list('num_matches', flat=True))
            
            # stories = stories.filter(*filter_conditions, num_matches__gt = matches_median).order_by(sort_by)[:100]
        else:
            stories = Post.objects.filter(*filter_conditions).order_by(sort_by)[:100]
        
        paginated_stories = Paginator(stories, per_page=10)
        get_page = paginated_stories.get_page(req_page)
        

        response = {
                "page": {
                    "current": get_page.number,
                    "total": paginated_stories.num_pages,
                    "has_next": get_page.has_next(),
                    "has_previous": get_page.has_previous(),
                },
                "stories": StoriesSerializer(get_page.object_list, many=True).data
        }
        
        return Response({"success": True, "data": response, "message": ""})

#Create or Update story
class ManipulateStory(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsAuthenticatedWriter,)
    
    def post(self, request):
        data = request.data
        genre = data.get('genre', None)
        descr = data.get('description', None)
        image = data.get('image', None)
        title = data.get('title', None)
        body = data.get('body', None)
        tags = data.get('tags', None)
        
        user = BaseUserProfile.objects.get(user = request.user)
        
        if genre == None or title == None or body == None:
            return Response({"success": False, "data": {}, "message": "missing genre, title or body"})
        
        
        try:
            genre = PostGenre.objects.get(genre = genre)
        except PostGenre.DoesNotExist:
            return Response({"success": False, "data": {}, "message": f"genre with genre={genre} does not exist"}) 
        
        create_story = Post(creator_id = user.writer, post_title = title, post_text = body, genre=genre)
        create_story.save()
        
        if descr:
            create_story.post_description = descr
        
        if image:
            create_story.post_image = image
        
        if tags:
            all_tags_query = []
            all_tags = tags.split(',')[:-1]
            for tag in all_tags:
                try:
                    get_tag = PostTags.objects.filter(tag = tag)
                except PostTags.DoesNotExist:
                    get_tag = PostTags(tag = tag)
                
                all_tags_query.append(get_tag)
                
            for tag in all_tags_query:
                create_story.tags.add(tag)
        
        create_story.save()
        
        return Response({"success": True, "data": {}, "message": "story created successfully"})
            
    def patch(self, request):
        data = request.data
        
        story_id = data.get('story_id', None)
        user = BaseUserProfile.objects.get(user = request.user)
        
        
        if story_id:
            try:
                story = Post.objects.get(pk = int(story_id))
            except Post.DoesNotExist:
                return Response({"success": False, "data": {}, "message": f"story with id={story_id} does not exist"})
        else:
            return Response({"success": False, "data": {}, "message": f"missing story_id"})
        
        if user.writer != story.creator_id:
            return Response({"success": False, "data": {}, "message": f"you can only edit your own stories"})
        
        genre = data.get('genre', None)
        descr = data.get('description', None)
        image = data.get('image', None)
        title = data.get('title', None)
        body = data.get('body', None)
        tags = data.get('tags', None)
        
        if genre:
            story.genre = PostGenre.objects.get(genre = genre)
        
        if descr:
            story.post_description = descr
        
        if image:
            story.post_image = image
        
        if title:
            story.post_title = title
        
        if body:
            story.post_text = body
        
        if tags:
            story.tags.clear()
            all_tags_query = []
            all_tags = tags.split(',')[:-1]
            for tag in all_tags:
                try:
                    get_tag = PostTags.objects.get(tag = tag)
                except PostTags.DoesNotExist:
                    get_tag = PostTags(tag = tag)
                    get_tag.save()
                
                all_tags_query.append(get_tag)
                
            for tag in all_tags_query:
                story.tags.add(tag)

        story.save()
        return Response({"success": True, "data": {}, "message": "story updated successfully"})

    def delete(self, request):
        story_id = request.data.get("story_id", None)
        
        if story_id == None:
            return Response({"success": False, "data": {}, "message": f"story_id is not passed in request body"})
        
        try:
            post = Post.objects.get(pk = int(story_id))
        except Post.DoesNotExist:
            return Response({"success": False, "data": {}, "message": f"story with specified story_id={story_id} does not exist"})
        
        base_user = BaseUserProfile.objects.get(user = request.user)
        
        if post.creator_id == base_user.writer:
            post.delete()
            return Response({"success": True, "data": {}, "message": "story deleted successfully"})
        else:
            return Response({"success": True, "data": {}, "message": "you do not have permission to delete this story (you must be story creator)"})

#Fetch all genres  
class GetGenres(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        req_page = int(request.GET.get('page', 1))
        order_by = request.GET.get("order_by", '-popularity')
        
        genres = PostGenre.objects.annotate(popularity = Count('post')).order_by(order_by)         #annotate(popularity = Count('post')).order_by('popularity')[:10]
        
        paginated_tags = Paginator(genres, per_page=10)
        get_page = paginated_tags.get_page(req_page)
        

        response = {
                "page": {
                    "current": get_page.number,
                    "total": paginated_tags.num_pages,
                    "has_next": get_page.has_next(),
                    "has_previous": get_page.has_previous(),
                },
                "stories": GenreSerializer(get_page.object_list, many=True).data
        }
        
        return Response({"success": True, "data": response, "message": ""})

#Fetch all tags
class GetTags(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        req_page = int(request.GET.get('page', 1))
        order_by = request.GET.get("order_by", '-popularity')
        
        tags = PostTags.objects.annotate(popularity = Count('post')).order_by(order_by)        #annotate(popularity = Count('post')).order_by('popularity')[:10]
        
        paginated_tags = Paginator(tags, per_page=10)
        get_page = paginated_tags.get_page(req_page)
        

        response = {
                "page": {
                    "current": get_page.number,
                    "total": paginated_tags.num_pages,
                    "has_next": get_page.has_next(),
                    "has_previous": get_page.has_previous(),
                },
                "stories": TagSerializer(get_page.object_list, many=True).data
        }
        
        return Response({"success": True, "data": response, "message": ""})
   
#Fetch all stories made by writer      
class GetWriterStories(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, IsAuthenticatedWriter,)
    
    def get(self, request):
        req_page = int(request.GET.get('page', 1))
        user = BaseUserProfile.objects.get(user = request.user)
        stories = Post.objects.filter(creator_id = user.writer)
        
        paginated_stories = Paginator(stories, per_page=10)
        get_page = paginated_stories.get_page(req_page)
        

        response = {
                "page": {
                    "current": get_page.number,
                    "total": paginated_stories.num_pages,
                    "has_next": get_page.has_next(),
                    "has_previous": get_page.has_previous(),
                },
                "stories": StoriesSerializer(get_page.object_list, many=True).data
        }
        
        return Response({"success": True, "data": response, "message": ""})
 
#Fetch all viewed stories   
class GetViewHistory(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
        req_page = int(request.GET.get('page', 1))
        user = BaseUserProfile.objects.get(user = request.user)
        
        get_viewed = UserViewedPosts.objects.get(reader=user.reader)
        
        paginated_stories = Paginator(get_viewed.posts.all(), per_page=10)
        get_page = paginated_stories.get_page(req_page)
        

        response = {
            "page": {
                "current": get_page.number,
                "total": paginated_stories.num_pages,
                "has_next": get_page.has_next(),
                "has_previous": get_page.has_previous(),
            },
            "stories": StoriesSerializer(get_page.object_list, many=True).data
        }
        
        return Response({"success": True, "data": response, "message": ""})
    
#Fetch distinct story
class GetSingleStory(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        data = request.GET
        
        id = data.get("story_id", None)
        
        if id == None:
            return Response({"success": False, "data": {}, "message": "No story_id was provided"})

        try:
            post = Post.objects.get(pk=int(id))
        except Post.DoesNotExist:
            return Response({"success": False, "data": {}, "message": f"Story with story_id={id} does not exist"})
        
        check_subscription = False
        check_ownership = False
        
        #highlight = request.GET.get('comment', None)
        auth = False
        notified = False
        
        if request.user.is_authenticated:
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
                        post.creator_id.save()
                        get_reader_posts.posts.add(post)
                        get_reader_posts.save()
                        request.session.save()

            try:
                notified = SubscriptionTimeStampThrough.objects.get(writer = post.creator_id, reader = user_profile.reader).receive_notifications
            except SubscriptionTimeStampThrough.DoesNotExist:
                notified = False
        
        context = {
            "story":StoriesSerializer(post).data,
            "subscribed": check_subscription ,
            "owner": check_ownership,
            "authenticated": auth,
            "get_notifications": notified, 
        }

        return Response({"success": True, "data": context, "message": ""})

#React to story    
class ReactToStory(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
     
    def post(self, request):
        data = request.data
        story_id = data.get('story_id', None)
        
        if story_id == None:
            return Response({"success": False, "data": {}, "message": "No story_id was provided"})
        
        try:
            story = Post.objects.get(pk=int(story_id))
        except Post.DoesNotExist:
            return Response({"success": False, "data": {}, "message": f"post with story_id={story_id} does not exist"})
        
        user = BaseUserProfile.objects.get(user = request.user)
        
        if user.writer:
            if user.writer == story.creator_id:
                return JsonResponse({"success": False, 'reactions': {'likes': story.likes_count, 'dislikes':story.dislikes_count}, 'reason': "You cannot like or dislike your own stories"}) 
        
        sessionData = request.session.get('story_like_variable')
        
        react_type = data.get('type', None)
        if react_type == None:
            return Response({"success": False, "data": {}, "message": "No type was provided ('like' or 'dislike' is required)"})
        
        string_story_id = str(story_id)
        
        
        reader_liked_stories = UserLikedPosts.objects.get(reader = user.reader)
            
        if sessionData == None:
            request.session['story_like_variable'] = {
                    'dislikes': {},
                }
            request.session.save()
            sessionData = request.session.get('story_like_variable')
        
        if react_type == 'like':  
            if story in reader_liked_stories.posts.all():
                reader_liked_stories.posts.remove(story)
                story.likes_count -= 1
                story.creator_id.total_likes_counter -= 1    
            else:
                reader_liked_stories.posts.add(story)
                story.likes_count += 1
                story.creator_id.total_likes_counter += 1      
                
                if string_story_id in sessionData['dislikes'].keys():
                    story.dislikes_count -= 1
                    story.creator_id.total_dislikes_counter -= 1

                    sessionData['dislikes'].pop(string_story_id, None)
        
        elif react_type == 'dislike':
            if string_story_id in sessionData['dislikes'].keys():
                story.dislikes_count -= 1
                story.creator_id.total_dislikes_counter -= 1
                sessionData['dislikes'].pop(string_story_id, None)
            else:
                story.dislikes_count += 1
                story.creator_id.total_dislikes_counter += 1
                sessionData['dislikes'].update({story_id: True})
                
                if story in reader_liked_stories.posts.all():
                    reader_liked_stories.posts.remove(story)
                    story.likes_count -= 1
                    story.creator_id.total_likes_counter -= 1
        else:
            return Response({"success": False, "data": {}, "message": "Invalid type provided ('like' or 'dislike' is required)"})       
                    
        request.session.save()
        story.save()
        reader_liked_stories.save()
        #print(sessionData)
        return Response({"success": True, "data": {'likes': story.likes_count, 'dislikes':story.dislikes_count}, "message": ""})   

#Fetch Liked Stories
class GetLikedStories(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        req_page = int(request.GET.get('page', 1))
        user = BaseUserProfile.objects.get(user = request.user)
        
        get_viewed = UserLikedPosts.objects.get(reader=user.reader)
        
        paginated_stories = Paginator(get_viewed.posts.all(), per_page=10)
        get_page = paginated_stories.get_page(req_page)
        

        response = {
            "page": {
                "current": get_page.number,
                "total": paginated_stories.num_pages,
                "has_next": get_page.has_next(),
                "has_previous": get_page.has_previous(),
            },
            "stories": StoriesSerializer(get_page.object_list, many=True).data
        }
        
        return Response({"success": True, "data": response, "message": ""})
            

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