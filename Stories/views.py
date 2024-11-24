from .models import *
from django.db.models import Count, Case, When, IntegerField
from django.http import JsonResponse
from django.core.paginator import Paginator
from Authentication.models import BaseUserProfile, SubscriptionTimeStampThrough
from django.db.models import Q, Count, Case, When, IntegerField
from statistics import median
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import StoriesSerializer, GenreSerializer, TagSerializer, AllStorySerializer
from .permissions import IsAuthenticatedWriter
from functools import reduce
import operator
from django.utils import timezone
from datetime import timedelta
from django.db.models import Value

#Fetch all stories there is (plus search)
class GetAllStories(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request):
        req_page = int(request.GET.get('page', 1))
        search_prompt = request.GET.get('search_prompt', None)
        genres = request.GET.get('genres', None)
        tags = request.GET.get('tags', None)
        sort_by = request.GET.get('sort_by', None)
        filter_conditions = []
        
        if not sort_by:
            sort_by = 'likes_count'
        
        if genres:
            genres_ids = list(map(int, genres.split(',')[:-1]))
            genre_condition = Q(genre__id__in = genres_ids)
            filter_conditions.append(genre_condition)

        if tags:
            genres_ids = list(map(int, tags.split(',')[:-1]))
            tag_condition = Q(tags__id__in = genres_ids)
            filter_conditions.append(tag_condition)

        try:
            filter_conditions = reduce(operator.and_, filter_conditions)
        except TypeError:
            filter_conditions = Q(*filter_conditions)
        
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
            stories = Post.objects.annotate(num_matches=sum(case_list))
            
            matches_median = median(stories.values_list('num_matches', flat=True))
            
            # if request.user.is_authenticated:
            #     stories = stories.filter(filter_conditions & Q(num_matches__gt = (matches_median / 2)**2)).annotate(priority=Value(4, output_field=models.IntegerField()))
            # else:
            stories = stories.filter(filter_conditions & Q(num_matches__gt = (matches_median / 2)**2)).order_by("-num_matches")
           
            #stories = stories.filter(filter_conditions).order_by("-num_matches")
        else:
            if sort_by == 'likes_count' or sort_by == '-likes_count':
                stories = Post.objects.filter(filter_conditions).alias(likes_count = Count('likes')).order_by(sort_by).annotate(priority=Value(2, output_field=models.IntegerField()))
            elif sort_by == 'views_counter' or sort_by == '-views_counter':
                stories = Post.objects.filter(filter_conditions).alias(views_counter = Count('views')).order_by(sort_by).annotate(priority=Value(2, output_field=models.IntegerField()))
            else:
                stories = Post.objects.filter(filter_conditions).order_by(sort_by).annotate(priority=Value(2, output_field=models.IntegerField()))
            
            # if request.user.is_authenticated and req_page == 1:
            #     stories = build_reader_profile_response_data(request.user, stories, False)
             
        paginated_stories = Paginator(stories[:200], per_page=20)
        get_page = paginated_stories.get_page(req_page)
        

        response = {
                "page": {
                    "current": get_page.number,
                    "total": paginated_stories.num_pages,
                    "has_next": get_page.has_next(),
                    "has_previous": get_page.has_previous(),
                },
                "stories": AllStorySerializer(get_page.object_list, many=True).data
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
            all_tags = tags.split(',')[:-1]
            for tag in all_tags:
                try:
                    get_tag = PostTags.objects.get(tag = tag)
                except PostTags.DoesNotExist:
                    get_tag = PostTags(tag = tag)
                
                create_story.tags.add(get_tag)
                
        create_story.save()
        
        return Response({"success": True, "data": StoriesSerializer(create_story).data, "message": "story created successfully"})
            
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
        
        msg = ""
        
        if genre:
            try:
                story.genre = PostGenre.objects.get(genre = genre)
                msg += "Genre updated. "
            except PostGenre.DoesNotExist:
                msg += f"Genre with genre={genre} does not exist. "
        
        if descr:
            story.post_description = descr
            msg += "Post description updated. "
        
        if image:
            story.post_image = image
            msg += "Post image updated. "
        
        if title:
            story.post_title = title
            msg += "Post title updated. "
        
        if body:
            story.post_text = body
            msg += "Post text updated. "
        
        if tags:
            story.tags.clear()
            all_tags_query = []
            all_tags = tags.split(',')[:-1]
            for tag in all_tags:
                try:
                    get_tag = PostTags.objects.get(tag = tag)
                    msg += f"Tag '{tag}' exists and was added. "
                except PostTags.DoesNotExist:
                    get_tag = PostTags(tag = tag)
                    get_tag.save()
                    msg += f"Tag '{tag}' does not exist. It was created and added. "
                
                all_tags_query.append(get_tag)
                
            for tag in all_tags_query:
                story.tags.add(tag)

        story.save()
        return Response({"success": True, "data": StoriesSerializer(story).data, "message": "Story updated successfully. " + msg})

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
        
        paginated_tags = Paginator(genres, per_page=20)
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
        
        paginated_tags = Paginator(tags, per_page=20)
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
        author_id = request.GET.get('author_id', None)
        
        if author_id != None:
            try:
                stories = Post.objects.filter(creator_id__id = int(author_id))
            except:
                return Response({"success": False, "data": {}, "message": "Either author_id is not int or requested profile has no writer profile"})
        else:
            user = BaseUserProfile.objects.get(user = request.user)
            
            try:
                stories = Post.objects.filter(creator_id = user.writer)
            except:
                return Response({"success": False, "data": {}, "message": "Requested profile has no writer profile"})
            
        paginated_stories = Paginator(stories, per_page=20)
        get_page = paginated_stories.get_page(req_page)
        

        response = {
                "page": {
                    "current": get_page.number,
                    "total": paginated_stories.num_pages,
                    "has_next": get_page.has_next(),
                    "has_previous": get_page.has_previous(),
                },
                "stories": AllStorySerializer(get_page.object_list, many=True).data
        }
        
        return Response({"success": True, "data": response, "message": ""})
 
#Fetch all viewed stories   
class GetViewHistory(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
        req_page = int(request.GET.get('page', 1))
        base_user = BaseUserProfile.objects.get(user = request.user)
        
        get_viewed = Post.objects.filter(views = base_user)
        
        paginated_stories = Paginator(get_viewed, per_page=20)
        get_page = paginated_stories.get_page(req_page)
        

        response = {
            "page": {
                "current": get_page.number,
                "total": paginated_stories.num_pages,
                "has_next": get_page.has_next(),
                "has_previous": get_page.has_previous(),
            },
            "stories": AllStorySerializer(get_page.object_list, many=True).data
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
        check_auth = False
        check_notified = False
        check_liked = False
        check_disliked = False
        
        if request.user.is_authenticated:
            check_auth = True
            user_profile = BaseUserProfile.objects.get(user = request.user)
            check_subscription = post.creator_id in user_profile.reader.subscribed_to.all()
            
            if user_profile not in post.views.all():
                post.views.add(user_profile)
                post.save()
                
            if user_profile.writer:
                check_ownership = post.creator_id == user_profile.writer

            try:
                check_notified = SubscriptionTimeStampThrough.objects.get(writer = post.creator_id, reader = user_profile.reader).receive_notifications
            except SubscriptionTimeStampThrough.DoesNotExist:
                check_notified = False
        
        context = {
            "story": StoriesSerializer(post).data,
            "liked": check_liked,
            "disliked": check_disliked,  
            "subscribed": check_subscription,
            "owner": check_ownership,
            "authenticated": check_auth,
            "get_notifications": check_notified, 
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
                return JsonResponse({"success": False, 'data': {}, 'reason': "You cannot like or dislike your own stories"}) 
        
        react_type = data.get('type', None)
        if react_type == None:
            return Response({"success": False, "data": {}, "message": "No type was provided ('like' or 'dislike' is required)"})
        
        if react_type == 'like':  
            if user in story.dislikes.all():
                story.dislikes.remove(user)
                
            if user in story.likes.all():
                story.likes.remove(user)
                msg = "Story like removed."
            else:
                story.likes.add(user)
                msg = "Story like added."
        elif react_type == 'dislike':
            if user in story.likes.all():
                story.likes.remove(user)
            
            if user in story.dislikes.all():
                story.dislikes.remove(user)
                msg = "Story dislike removed."
            else:
                story.dislikes.add(user)
                msg = "Story dislike added."
        else:
            return Response({"success": False, "data": {}, "message": "Invalid type provided ('like' or 'dislike' is required)"})       
                    
        #print(sessionData)
        story.save()
        return Response({"success": True, "data": StoriesSerializer(story).data, "message": msg})   

#Fetch Liked Stories
class GetLikedStories(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        req_page = int(request.GET.get('page', 1))
        base_user = BaseUserProfile.objects.get(user = request.user)
        
        get_liked = Post.objects.filter(likes = base_user)
        
        paginated_stories = Paginator(get_liked, per_page=20)
        get_page = paginated_stories.get_page(req_page)
        

        response = {
            "page": {
                "current": get_page.number,
                "total": paginated_stories.num_pages,
                "has_next": get_page.has_next(),
                "has_previous": get_page.has_previous(),
            },
            "stories": AllStorySerializer(get_page.object_list, many=True).data
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
    q_query = Q(post_title__icontains = init) | Q(post_description__icontains = init)
    search_query[q_query] = len(init)
    
    for word in tokenized:
        q_query = Q(post_title__icontains = word) | Q(post_description__icontains = word)
        search_query[q_query] = len(word)
        for j in range(1, len(word)):
            key1 = word[:-j]
            key2 = word[j:]
            q_query = Q(post_title__icontains = key1) | Q(post_description__icontains = key1)
            search_query[q_query] = len(key1) + 1
            
            q_query = Q(post_title__icontains = key1) | Q(post_description__icontains = key1)
            search_query[q_query] = len(key2)

    return search_query

def build_reader_profile_response_data(user, initial_query, search=False):
    base_user = BaseUserProfile.objects.get(user = user)
    
    subscriptions = base_user.reader.subscribed_to.all()
    liked = Post.objects.filter(likes=base_user)
    viewed = Post.objects.filter(views=base_user)

    if search:
        return initial_query
    else:
        one_week_ago = timezone.now() - timedelta(weeks=1)
        get_subscription_newest = Post.objects.filter(creator_id__in=subscriptions, created__gte=one_week_ago).exclude(views=base_user).annotate(priority=Value(4, output_field=models.IntegerField())).order_by("-created")

        prefered_genres = dict()
        prefered_tags = dict()
        combined_dataset = liked.union(viewed)
        
        for post in combined_dataset:
            if post.tags in prefered_tags.keys():
                prefered_genres[post.tags] += 1
            else:
                prefered_genres[post.tags] = 1
                
            if post.genre in prefered_genres.keys():
                prefered_genres[post.genre] += 1
            else:
                prefered_genres[post.genre] = 1

        # viewed / liked ratio - % of viewed posts that user liked - haven't found a use for this yet :(
        # satisfaction_rate = len(combined_dataset) / (len(liked) + len(viewed)) if len(combined_dataset) > 0 else 1
        
        try:
            # get median of all watched and liked tags
            genres_rate = sum(prefered_genres.values()) / len(prefered_genres)
            tags_rate = sum(prefered_tags.values()) / len(prefered_tags)
            
            # fetch most viewed genres and tags
            prefered_genres = [key for key in prefered_genres.keys() if prefered_genres[key] >= genres_rate]
            prefered_tags = [key for key in prefered_tags.keys() if prefered_tags[key] >= tags_rate]

            prefered_prediction = Post.objects.filter(Q(genre__in=prefered_genres) | Q(tags__in=prefered_tags))
            
            final_dataset = (initial_query | get_subscription_newest | prefered_prediction).distinct().order_by("-priority")
        except ZeroDivisionError:
            final_dataset = (initial_query | get_subscription_newest).distinct().order_by("-priority")
        
        return final_dataset

        
    
    
    
    
    
    
    
    
    