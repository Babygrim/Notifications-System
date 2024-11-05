from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('all', GetAllStories.as_view(), name='get_all_stories'),
    path('create', ManipulateStory.as_view(), name='createstory'),
    path('get_genres', GetGenres.as_view(), name='genres'),
    path('get_tags', GetTags.as_view(), name='tags'),
    path('single', GetSingleStory.as_view(), name='story_page'),
    path('get_writer_stories', GetWriterStories.as_view(), name="writer_stories"),
    path('get_viewed', GetViewHistory.as_view(), name='getviews'),
    path('get_liked', GetLikedStories.as_view(), name='getlikes'),
    path('react', ReactToStory.as_view(), name='reaction'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
