from django.urls import path
from .views import *

urlpatterns = [
    path('all', GetComments.as_view(), name='get_comments_or_replies'),
    path('manipulate', CreateComments.as_view(), name='create_comments_or_replies'),
    path('react', LikeUnlikeComment.as_view(), name= "like_unlike"),
    
]
