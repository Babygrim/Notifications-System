from django.urls import path
from .views import *

urlpatterns = [
    
    path('all', GetNotifications.as_view(), name='getNotifications'),
    path('mark_as_read', MarkAsRead.as_view(), name='markAsRead'),
    
]
