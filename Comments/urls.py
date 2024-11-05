from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('all', GetComments.as_view(), name='get_comments_or_replies'),
    path('create', CreateComments.as_view(), name='create_comments_or_replies'),
    path('react', LikeUnlikeComment.as_view(), name= "likeunlike"),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
