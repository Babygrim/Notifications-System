from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('replies', getCommentReplies, name='make_comments'),
    path('comments', getStoryComments, name = "comments"),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
