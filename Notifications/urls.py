from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('all', GetNotifications.as_view(), name='getNotifications'),
    path('mark_as_read', MarkAsRead.as_view(), name='markAsRead'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
