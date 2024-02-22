from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', getAllStories, name="stories"),
    path('story/<int:id>', getSingleStory, name="story"),
    path('getStoryPage', getStoryPage, name="getstorypage"),
    path('createStory', createStory, name='createstory'),
    path('get_genres', getGenres, name='genres'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
