from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', getAllStories, name="stories"),
    path('story/<int:id>', getSingleStory, name="story"),
    path('get_story_page', getStoryPage, name="getstorypage"),
    path('create_story', createStory, name='createstory'),
    path('get_genres', getGenres, name='genres'),
    path('get_tags', getTags, name='tags'),
    path('get_distinct_story', getDistinctStoryPage, name='story_page'),
    path('get_writer_stories/<int:id>', getWriterStories, name="write_stories"),
    path('get_viewed', getUserViewHistory, name='getviews'),
    path('get_liked', getUserLikedStories, name='getlikes'),
    path('react_story', reactToStory, name='reaction'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
